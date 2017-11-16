"""
Created on 08.11.2017

Module for testing of the evaluating component

@author: Jonas Holtkamp
"""
import unittest

import datetime as dt

from definitions import DATASETS_DIR, JSON_DIR
from evaluating.evaluator_utils import read_portfolio
from utils import read_stock_market_data_conveniently
from utils import read_stock_market_data
from evaluating.portfolio_evaluator import PortfolioEvaluator
from model.CompanyEnum import CompanyEnum
from model.Portfolio import Portfolio
from model.StockMarketData import StockMarketData
from predicting.predictor.simple_predictor import SimplePredictor
from predicting.predictor.perfect_predictor import PerfectPredictor
from trading.trader.simple_trader import SimpleTrader
from trading.model.trader_interface import SharesOfCompany, TradingActionList


class EvaluatorTest(unittest.TestCase):
    def testReadPortfolio(self):
        """
        Tests: evaluator_utils.py/read_portfolio

        Read "../json/portfolio.json" and check if that happens correctly
        """
        portfolio = read_portfolio(path=JSON_DIR)

        self.assertEqual(len(portfolio.shares), 2)
        self.assertEqual(portfolio.cash, 10000.0)
        self.assertEqual(portfolio.shares[0].company_enum, CompanyEnum.COMPANY_B)

    def testReadStockMarketData(self):
        """
        Tests: evaluator_utils.py/read_stock_market_data

        Read "../datasets/[AAPL|GOOG].csv" and check if that happens correctly
        """
        apple = 'AAPL'
        google = 'GOOG'

        stock_market_data = read_stock_market_data(
            [[CompanyEnum.COMPANY_A, apple], [CompanyEnum.COMPANY_B, google]], DATASETS_DIR)

        self.assertGreater(len(stock_market_data.market_data), 0)
        self.assertTrue(CompanyEnum.COMPANY_A in stock_market_data.market_data)
        self.assertTrue(CompanyEnum.COMPANY_B in stock_market_data.market_data)

    def testGetMostRecentTradeDay(self):
        """
        Tests: StockMarketData#get_most_recent_trade_day

        Read the stock market data and check if the last available date is determined correctly
        """
        apple = 'AAPL'
        google = 'GOOG'

        stock_market_data = read_stock_market_data(
            [[CompanyEnum.COMPANY_A, apple], [CompanyEnum.COMPANY_B, google]], DATASETS_DIR)

        self.assertEqual(stock_market_data.get_most_recent_trade_day(),
                         stock_market_data.market_data[CompanyEnum.COMPANY_A][-1][0])

    def testDoTrade(self):
        """
        Tests: SimpleTrader#doTrade

        Reads the available portfolio and stock market data of AAPL and executes one trade. Checks if the action list
        is not empty
        """
        symbol = 'AAPL'

        trader = SimpleTrader(PerfectPredictor(CompanyEnum.COMPANY_A), None)
        current_portfolio_value = 0.0  # Dummy value
        portfolio = read_portfolio(path=JSON_DIR)
        trading_action_list = trader.doTrade(portfolio, current_portfolio_value,
                                             read_stock_market_data([[CompanyEnum.COMPANY_A, symbol]],
                                                                    DATASETS_DIR))

        self.assertTrue(trading_action_list is not None)
        self.assertTrue(trading_action_list.len(), 1)
        self.assertEqual(trading_action_list.get(0).shares.company_enum, CompanyEnum.COMPANY_A)

    def testUpdatePortfolio_noSufficientCashReserve(self):
        """
        Tests: Portfolio#update

        Flavour: Not enough cash in the portfolio, so no trades should be applied

        Creates a portfolio, a stock market data object and a arbitrary `TradingActionList` and executes this trading
        actions on the portfolio. Checks if those are applied correctly
        """
        cash_reserve = 10000.0

        data = list()
        data.append(('2017-01-01', 150.0))
        stock_market_data = StockMarketData({CompanyEnum.COMPANY_A: data})

        portfolio = Portfolio(cash_reserve, [SharesOfCompany(CompanyEnum.COMPANY_A, 200)])
        trading_action_list = TradingActionList()
        trading_action_list.buy(CompanyEnum.COMPANY_A, 100)

        updated_portfolio = portfolio.update(stock_market_data, trading_action_list)

        # Trade volume is too high for current cash reserve. Nothing should happen
        self.assertEqual(updated_portfolio.cash, cash_reserve)
        self.assertEqual(updated_portfolio.cash, portfolio.cash)
        self.assertEqual(updated_portfolio.shares[0].company_enum, CompanyEnum.COMPANY_A)
        self.assertEqual(updated_portfolio.shares[0].amount, 200)

    def testUpdatePortfolio_sufficientCashReserve(self):
        """
        Tests: Portfolio#update

        Flavour: Enough cash in the portfolio, so the trades should be applied

        Creates a portfolio, a stock market data object and a arbitrary `TradingActionList` and executes this trading
        actions on the portfolio. Checks if those are applied correctly
        """
        cash_reserve = 20000.0

        data = list()
        data.append(('2017-01-01', 150.0))
        stock_market_data = StockMarketData({CompanyEnum.COMPANY_A: data})

        portfolio = Portfolio(cash_reserve, [SharesOfCompany(CompanyEnum.COMPANY_A, 200)])

        trading_action_list = TradingActionList()
        trading_action_list.buy(CompanyEnum.COMPANY_A, 100)

        updated_portfolio = portfolio.update(stock_market_data, trading_action_list)

        # Current cash reserve is sufficient for trade volume. Trade should happen
        self.assertLess(updated_portfolio.cash, cash_reserve)
        self.assertLess(updated_portfolio.cash, portfolio.cash)
        self.assertEqual(updated_portfolio.shares[0].company_enum, CompanyEnum.COMPANY_A)
        self.assertEqual(updated_portfolio.shares[0].amount, 300)

    def testUpdateAndDraw(self):
        """
        Tests: Evaluator#inspect_over_time

        Creates a portfolio, a stock market data object
        """
        trader = SimpleTrader(SimplePredictor(), SimplePredictor())

        evaluator = PortfolioEvaluator([trader] * 3, draw_results=False)

        full_stock_market_data = read_stock_market_data_conveniently([CompanyEnum.COMPANY_A, CompanyEnum.COMPANY_B],
                                                                     ['1962-2011', '2012-2017'])

        # Calculate and save the initial total portfolio value (i.e. the cash reserve)
        portfolio1 = Portfolio(50000.0, [], 'portfolio 1')
        portfolio2 = Portfolio(100000.0, [], 'portfolio 2')
        portfolio3 = Portfolio(150000.0, [], 'portfolio 3')

        portfolios_over_time = evaluator.inspect_over_time(full_stock_market_data, [portfolio1, portfolio2, portfolio3],
                                                           evaluation_offset=100)

        last_date = list(portfolios_over_time['portfolio 1'].keys())[-1]
        self.assertEqual(last_date, dt.datetime.strptime('2017-11-07', '%Y-%m-%d').date())

        data_row_lengths = set([len(value_set) for value_set in portfolios_over_time.values()])
        self.assertEqual(len(data_row_lengths), 1)
        self.assertEqual(data_row_lengths.pop(), 100)

    def testReadData_2stocks_2periods(self):
        period1 = '1962-2011'
        period2 = '2012-2017'

        test = read_stock_market_data_conveniently([CompanyEnum.COMPANY_A, CompanyEnum.COMPANY_B], [period1, period2])

        self.assertEqual(len(test.market_data), 2)
        self.assertTrue(CompanyEnum.COMPANY_A in test.market_data.keys())
        self.assertTrue(CompanyEnum.COMPANY_B in test.market_data.keys())

    def testReadData_2stocks_1period(self):
        period1 = '1962-2011'

        test = read_stock_market_data_conveniently([CompanyEnum.COMPANY_A, CompanyEnum.COMPANY_B], [period1])

        self.assertEqual(len(test.market_data), 2)
        self.assertTrue(CompanyEnum.COMPANY_A in test.market_data.keys())
        self.assertTrue(CompanyEnum.COMPANY_B in test.market_data.keys())

    def testReadData_2stocks_noPeriods(self):
        test = read_stock_market_data_conveniently([CompanyEnum.COMPANY_A, CompanyEnum.COMPANY_B], [])

        self.assertEqual(len(test.market_data), 2)
        self.assertTrue(CompanyEnum.COMPANY_A in test.market_data.keys())
        self.assertTrue(CompanyEnum.COMPANY_B in test.market_data.keys())

    def testReadData_1stock_2periods(self):
        period1 = '1962-2011'
        period2 = '2012-2017'

        test = read_stock_market_data_conveniently([CompanyEnum.COMPANY_B], [period1, period2])

        self.assertEqual(len(test.market_data), 1)
        self.assertTrue(CompanyEnum.COMPANY_B in test.market_data.keys())

    def testReadData_1stock_noPeriods(self):
        test = read_stock_market_data_conveniently([CompanyEnum.COMPANY_B], [])

        self.assertEqual(len(test.market_data), 1)
        self.assertTrue(CompanyEnum.COMPANY_B in test.market_data.keys())


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(EvaluatorTest)
    unittest.TextTestRunner(verbosity=2).run(suite)
