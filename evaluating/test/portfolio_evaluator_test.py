"""
Created on 08.11.2017

Module for testing of the evaluating component

@author: Jonas Holtkamp
"""
import unittest

from datetime import date, datetime

from model.StockData import StockData
from utils import read_stock_market_data
from evaluating.portfolio_evaluator import PortfolioEvaluator
from model.CompanyEnum import CompanyEnum
from model.Portfolio import Portfolio
from model.StockMarketData import StockMarketData
from predicting.predictor.random_predictor import RandomPredictor
from predicting.predictor.perfect_predictor import PerfectPredictor
from trading.trader.simple_trader import SimpleTrader
from model.trader_actions import SharesOfCompany, TradingActionList


class EvaluatorTest(unittest.TestCase):
    def testUpdateAndDraw(self):
        """
        Tests: Evaluator#inspect_over_time

        Creates a portfolio, a stock market data object
        """
        trader = SimpleTrader(RandomPredictor(), RandomPredictor())

        evaluator = PortfolioEvaluator([trader] * 3, draw_results=False)

        full_stock_market_data = read_stock_market_data([CompanyEnum.COMPANY_A, CompanyEnum.COMPANY_B],
                                                        ['1962-2011', '2012-2017'])

        # Calculate and save the initial total portfolio value (i.e. the cash reserve)
        portfolio1 = Portfolio(50000.0, [], 'portfolio 1')
        portfolio2 = Portfolio(100000.0, [], 'portfolio 2')
        portfolio3 = Portfolio(150000.0, [], 'portfolio 3')

        portfolios_over_time = evaluator.inspect_over_time(full_stock_market_data, [portfolio1, portfolio2, portfolio3],
                                                           evaluation_offset=100)

        last_date = list(portfolios_over_time['portfolio 1'].keys())[-1]
        self.assertEqual(last_date, datetime.strptime('2017-11-06', '%Y-%m-%d').date())

        data_row_lengths = set([len(value_set) for value_set in portfolios_over_time.values()])
        self.assertEqual(len(data_row_lengths), 1)
        self.assertEqual(data_row_lengths.pop(), 100)

    def test_inspect_with_default_offset(self):
        data = StockData([(date(2017, 1, 1), 150.0), (date(2017, 1, 2), 200.0), (date(2017, 1, 3), 250.0)])
        stock_market_data = StockMarketData({CompanyEnum.COMPANY_A: data})

        portfolio = Portfolio(20000, [SharesOfCompany(CompanyEnum.COMPANY_A, 200)])

        evaluator = PortfolioEvaluator([SimpleTrader(RandomPredictor(), RandomPredictor())])

        portfolio_over_time: dict = evaluator.inspect_over_time(stock_market_data, [portfolio], evaluation_offset=-1)[
            'nameless']

        self.assertTrue(date(2016, 12, 31) in portfolio_over_time.keys())
        self.assertTrue(date(2017, 1, 1) in portfolio_over_time.keys())
        self.assertTrue(date(2017, 1, 2) in portfolio_over_time.keys())
        self.assertTrue(date(2017, 1, 3) not in portfolio_over_time.keys())

    def test_inspect_with_date_offset(self):
        data = StockData([(date(2017, 1, 1), 150.0), (date(2017, 1, 2), 200.0), (date(2017, 1, 3), 250.0)])
        stock_market_data = StockMarketData({CompanyEnum.COMPANY_A: data})

        portfolio = Portfolio(20000, [SharesOfCompany(CompanyEnum.COMPANY_A, 200)])

        evaluator = PortfolioEvaluator([SimpleTrader(RandomPredictor(), RandomPredictor())])

        portfolio_over_time: dict = \
            evaluator.inspect_over_time(stock_market_data, [portfolio], date_offset=date(2017, 1, 2))['nameless']

        self.assertTrue(date(2016, 12, 31) not in portfolio_over_time.keys())
        self.assertTrue(date(2017, 1, 1) in portfolio_over_time.keys())
        self.assertTrue(date(2017, 1, 2) in portfolio_over_time.keys())
        self.assertTrue(date(2017, 1, 3) not in portfolio_over_time.keys())


class UtilsTest(unittest.TestCase):
    def testReadStockMarketData(self):
        """
        Tests: evaluator_utils.py/read_stock_market_data

        Read "../datasets/stock_[a|b]_[1962-2011|2012-2017].csv" and check if that happens correctly
        """
        stock_market_data = read_stock_market_data([CompanyEnum.COMPANY_A, CompanyEnum.COMPANY_B],
                                                   ['1962-2011', '2012-2017'])

        self.assertGreater(stock_market_data.get_number_of_companies(), 0)
        self.assertTrue(CompanyEnum.COMPANY_A in stock_market_data.get_companies())
        self.assertTrue(CompanyEnum.COMPANY_B in stock_market_data.get_companies())

    def testReadData_2stocks_2periods(self):
        period1 = '1962-2011'
        period2 = '2012-2017'

        test = read_stock_market_data([CompanyEnum.COMPANY_A, CompanyEnum.COMPANY_B], [period1, period2])

        self.assertEqual(test.get_number_of_companies(), 2)
        self.assertTrue(CompanyEnum.COMPANY_A in test.get_companies())
        self.assertTrue(CompanyEnum.COMPANY_B in test.get_companies())

    def testReadData_2stocks_1period(self):
        period1 = '1962-2011'

        test = read_stock_market_data([CompanyEnum.COMPANY_A, CompanyEnum.COMPANY_B], [period1])

        self.assertEqual(test.get_number_of_companies(), 2)
        self.assertTrue(CompanyEnum.COMPANY_A in test.get_companies())
        self.assertTrue(CompanyEnum.COMPANY_B in test.get_companies())

    def testReadData_2stocks_noPeriods(self):
        test = read_stock_market_data([CompanyEnum.COMPANY_A, CompanyEnum.COMPANY_B], [])

        self.assertEqual(test.get_number_of_companies(), 2)
        self.assertTrue(CompanyEnum.COMPANY_A in test.get_companies())
        self.assertTrue(CompanyEnum.COMPANY_B in test.get_companies())

    def testReadData_1stock_2periods(self):
        period1 = '1962-2011'
        period2 = '2012-2017'

        test = read_stock_market_data([CompanyEnum.COMPANY_B], [period1, period2])

        self.assertEqual(test.get_number_of_companies(), 1)
        self.assertFalse(CompanyEnum.COMPANY_A in test.get_companies())
        self.assertTrue(CompanyEnum.COMPANY_B in test.get_companies())

    def testReadData_1stock_noPeriods(self):
        test = read_stock_market_data([CompanyEnum.COMPANY_B], [])

        self.assertEqual(test.get_number_of_companies(), 1)
        self.assertFalse(CompanyEnum.COMPANY_A in test.get_companies())
        self.assertTrue(CompanyEnum.COMPANY_B in test.get_companies())


if __name__ == "__main__":
    suites = list()
    suites.append(unittest.TestLoader().loadTestsFromTestCase(EvaluatorTest))
    suites.append(unittest.TestLoader().loadTestsFromTestCase(UtilsTest))
    unittest.TextTestRunner(verbosity=2).run(unittest.TestSuite(suites))
