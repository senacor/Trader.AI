"""
Created on 08.11.2017

Module for testing of the evaluating component

@author: Jonas Holtkamp
"""
import unittest

import datetime as dt

from definitions import DATASETS_DIR, JSON_DIR
from evaluating.evaluator_utils import read_portfolio, read_stock_market_data
from evaluating.portfolio_evaluator import PortfolioEvaluator
from model.CompanyEnum import CompanyEnum
from model.Portfolio import Portfolio
from model.StockMarketData import StockMarketData
from predicting.simple_predictor import SimplePredictor
from predicting.perfect_stock_a_predictor import PerfectStockAPredictor
from trading.simple_trader import SimpleTrader
from trading.trader_interface import TradingAction, TradingActionEnum, SharesOfCompany, TradingActionList


class EvaluatorTest(unittest.TestCase):
    def testReadPortfolio(self):
        """
        Tests: evaluator_utils.py/read_portfolio

        Read "../json/portfolio.json" and check if that happens correctly
        """
        portfolio = read_portfolio(path=JSON_DIR)

        self.assertEqual(len(portfolio.shares), 2)
        self.assertEqual(portfolio.cash, 10000.0)
        self.assertEqual(portfolio.shares[0].name, CompanyEnum.COMPANY_B.value)

    def testReadStockMarketData(self):
        """
        Tests: evaluator_utils.py/read_stock_market_data

        Read "../datasets/[AAPL|GOOG].csv" and check if that happens correctly
        """
        apple = 'AAPL'
        google = 'GOOG'

        stock_market_data = read_stock_market_data(
            [[CompanyEnum.COMPANY_A.value, apple], [CompanyEnum.COMPANY_B.value, google]], DATASETS_DIR)

        self.assertGreater(len(stock_market_data.market_data), 0)
        self.assertTrue(CompanyEnum.COMPANY_A.value in stock_market_data.market_data)
        self.assertTrue(CompanyEnum.COMPANY_B.value in stock_market_data.market_data)

    def testGetMostRecentTradeDay(self):
        """
        Tests: StockMarketData#get_most_recent_trade_day

        Read the stock market data and check if the last available date is determined correctly
        """
        apple = 'AAPL'
        google = 'GOOG'

        stock_market_data = read_stock_market_data(
            [[CompanyEnum.COMPANY_A.value, apple], [CompanyEnum.COMPANY_B.value, google]], DATASETS_DIR)

        self.assertEqual(stock_market_data.get_most_recent_trade_day(),
                         stock_market_data.market_data[CompanyEnum.COMPANY_A.value][-1][0])

    def testDoTrade(self):
        """
        Tests: SimpleTrader#doTrade

        Reads the available portfolio and stock market data of AAPL and executes one trade. Checks if the action list
        is not empty
        """
        symbol = 'AAPL'

        trader = SimpleTrader(PerfectStockAPredictor(), None)
        current_portfolio_value = 0.0  # Dummy value
        portfolio = read_portfolio(path=JSON_DIR)
        trading_action_list = trader.doTrade(portfolio, current_portfolio_value,
                                             read_stock_market_data([[CompanyEnum.COMPANY_A.value, symbol]],
                                                                    DATASETS_DIR))

        self.assertTrue(trading_action_list is not None)
        self.assertTrue(trading_action_list.len(), 1)
        self.assertEqual(trading_action_list.get(0).shares.name, CompanyEnum.COMPANY_A.value)

    def testUpdatePortfolio_noSufficientCashReserve(self):
        """
        Tests: Portfolio#update

        Flavour: Not enough cash in the portfolio, so no trades should be applied

        Creates a portfolio, a stock market data object and a arbitrary `TradingActionList` and executes this trading
        actions on the portfolio. Checks if those are applied correctly
        """
        cash_reserve = 10000.0
        symbol = "AAPL"

        data = list()
        data.append(('2017-01-01', 150.0))
        stock_market_data = StockMarketData({symbol: data})

        portfolio = Portfolio(cash_reserve, [SharesOfCompany(symbol, 200)])
        trading_action_list = TradingActionList()
        trading_action_list.addTradingAction(TradingAction(TradingActionEnum.BUY, SharesOfCompany(symbol, 100)))

        updated_portfolio = portfolio.update(stock_market_data, trading_action_list)

        # Trade volume is too high for current cash reserve. Nothing should happen
        self.assertEqual(updated_portfolio.cash, cash_reserve)
        self.assertEqual(updated_portfolio.cash, portfolio.cash)
        self.assertEqual(updated_portfolio.shares[0].name, symbol)
        self.assertEqual(updated_portfolio.shares[0].amount, 200)

    def testUpdatePortfolio_sufficientCashReserve(self):
        """
        Tests: Portfolio#update

        Flavour: Enough cash in the portfolio, so the trades should be applied

        Creates a portfolio, a stock market data object and a arbitrary `TradingActionList` and executes this trading
        actions on the portfolio. Checks if those are applied correctly
        """
        cash_reserve = 20000.0
        symbol = "AAPL"

        data = list()
        data.append(('2017-01-01', 150.0))
        stock_market_data = StockMarketData({symbol: data})

        portfolio = Portfolio(cash_reserve, [SharesOfCompany(symbol, 200)])

        trading_action_list = TradingActionList()
        trading_action_list.addTradingAction(TradingAction(TradingActionEnum.BUY, SharesOfCompany(symbol, 100)))

        updated_portfolio = portfolio.update(stock_market_data, trading_action_list)

        # Current cash reserve is sufficient for trade volume. Trade should happen
        self.assertLess(updated_portfolio.cash, cash_reserve)
        self.assertLess(updated_portfolio.cash, portfolio.cash)
        self.assertEqual(updated_portfolio.shares[0].name, symbol)
        self.assertEqual(updated_portfolio.shares[0].amount, 300)

    def testUpdateAndDraw(self):
        """
        Tests: Evaluator#inspect_over_time

        Creates a portfolio, a stock market data object
        """
        trader = SimpleTrader(SimplePredictor(), SimplePredictor())

        evaluator = PortfolioEvaluator([trader] * 3, draw_results=False)

        stock_a = 'stock_a'
        stock_b = 'stock_b'

        full_stock_market_data = self.get_test_data(stock_a, stock_b)

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

    def get_test_data(self, stock_a, stock_b):
        period1 = '1962-2011'
        period2 = '2012-2017'

        # Reading in *all* available data
        data_a1 = read_stock_market_data([[CompanyEnum.COMPANY_A.value, ('%s_%s' % (stock_a, period1))]], DATASETS_DIR)
        data_a2 = read_stock_market_data([[CompanyEnum.COMPANY_A.value, ('%s_%s' % (stock_a, period2))]], DATASETS_DIR)
        data_b1 = read_stock_market_data([[CompanyEnum.COMPANY_B.value, ('%s_%s' % (stock_b, period1))]], DATASETS_DIR)
        data_b2 = read_stock_market_data([[CompanyEnum.COMPANY_B.value, ('%s_%s' % (stock_b, period2))]], DATASETS_DIR)

        # Combine both datasets to one StockMarketData object
        old_data_a = data_a1.market_data[CompanyEnum.COMPANY_A.value]
        new_data_a = data_a2.market_data[CompanyEnum.COMPANY_A.value]
        old_data_b = data_b1.market_data[CompanyEnum.COMPANY_B.value]
        new_data_b = data_b2.market_data[CompanyEnum.COMPANY_B.value]

        full_stock_market_data = StockMarketData({stock_a: old_data_a + new_data_a, stock_b: old_data_b + new_data_b})

        return full_stock_market_data


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(EvaluatorTest)
    unittest.TextTestRunner(verbosity=2).run(suite)
