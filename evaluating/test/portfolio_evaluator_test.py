"""
Created on 08.11.2017

Module for testing of the evaluating component

@author: Jonas Holtkamp
"""
import unittest

from datetime import date, datetime

from definitions import PERIOD_1, PERIOD_2, PERIOD_3
from model.StockData import StockData
from predicting.predictor.reference.perfect_predictor import PerfectPredictor
from utils import read_stock_market_data
from evaluating.portfolio_evaluator import PortfolioEvaluator
from model.CompanyEnum import CompanyEnum
from model.Portfolio import Portfolio
from model.StockMarketData import StockMarketData
from model.Order import SharesOfCompany
from predicting.predictor.reference.random_predictor import RandomPredictor
from trading.trader.reference.simple_trader import SimpleTrader


class EvaluatorTest(unittest.TestCase):
    def test_different_mappings(self):
        """
        Tests: Evaluator#inspect_over_time and #inspect_over_time_with_mappings

        Compares if both methods return the same values
        """
        stock_market_data = read_stock_market_data([CompanyEnum.COMPANY_A], [PERIOD_1, PERIOD_2, PERIOD_3])

        portfolio_1 = Portfolio(20000, [SharesOfCompany(CompanyEnum.COMPANY_A, 200)])
        portfolio_2 = Portfolio(20000, [SharesOfCompany(CompanyEnum.COMPANY_A, 200)])
        portfolios = [portfolio_1, portfolio_2]

        perfect_predictor = PerfectPredictor(CompanyEnum.COMPANY_A)

        trader_1 = SimpleTrader(perfect_predictor, perfect_predictor)
        trader_2 = SimpleTrader(perfect_predictor, perfect_predictor)
        trader_3 = SimpleTrader(RandomPredictor(), RandomPredictor())
        traders = [trader_1, trader_2]

        portfolio_trader_mappings = list(zip(portfolios, traders))

        evaluator_1 = PortfolioEvaluator([trader_1, trader_1])
        evaluator_2 = PortfolioEvaluator([])
        evaluator_3 = PortfolioEvaluator([trader_3, trader_3])

        # 1 Use evaluator that is initialized *with* traders and call `#inspect_over_time` (i.e. without traders)
        result_1 = evaluator_1.inspect_over_time(stock_market_data, portfolios, 100)

        # 2 Use evaluator that is initialized *without* traders and call `#inspect_over_time_with_mapping`
        # (i.e. with traders)
        result_2 = evaluator_2.inspect_over_time_with_mapping(stock_market_data, portfolio_trader_mappings, 100)

        # 3 Use evaluator that is initialized *with* traders and call `#inspect_over_time_with_mapping`
        # (i.e. with traders) - this should be no problem, because the traders given at initialization time are ignored
        result_3 = evaluator_3.inspect_over_time_with_mapping(stock_market_data, portfolio_trader_mappings, 100)

        assert result_1 == result_2 == result_3

    def test_update_and_draw(self):
        """
        Tests: Evaluator#inspect_over_time

        Inspects portfolios over time and checks the results
        """
        trader = SimpleTrader(RandomPredictor(), RandomPredictor())

        evaluator = PortfolioEvaluator([trader] * 3, draw_results=False)

        full_stock_market_data = read_stock_market_data([CompanyEnum.COMPANY_A, CompanyEnum.COMPANY_B],
                                                        [PERIOD_1, PERIOD_2, PERIOD_3])

        # Calculate and save the initial total portfolio value (i.e. the cash reserve)
        portfolio1 = Portfolio(50000.0, [], 'portfolio 1')
        portfolio2 = Portfolio(100000.0, [], 'portfolio 2')
        portfolio3 = Portfolio(150000.0, [], 'portfolio 3')

        portfolios_over_time = evaluator.inspect_over_time(full_stock_market_data, [portfolio1, portfolio2, portfolio3],
                                                           evaluation_offset=100)

        last_date = list(portfolios_over_time['portfolio 1'].keys())[-1]

        assert last_date == datetime.strptime('2017-11-06', '%Y-%m-%d').date()

        data_row_lengths = set([len(value_set) for value_set in portfolios_over_time.values()])
        assert len(data_row_lengths) == 1
        assert data_row_lengths.pop() == 100

    def test_inspect__default_offset(self):
        """
        Tests: Evaluator#inspect_over_time

        Flavour: Test with an int offset
        """
        data = StockData([(date(2017, 1, 1), 150.0), (date(2017, 1, 2), 200.0), (date(2017, 1, 3), 250.0)])
        stock_market_data = StockMarketData({CompanyEnum.COMPANY_A: data})

        portfolio = Portfolio(20000, [SharesOfCompany(CompanyEnum.COMPANY_A, 200)])

        evaluator = PortfolioEvaluator([SimpleTrader(RandomPredictor(), RandomPredictor())])

        portfolio_over_time: dict = evaluator.inspect_over_time(stock_market_data, [portfolio], evaluation_offset=-1)[
            'nameless']

        assert date(2016, 12, 31) in portfolio_over_time.keys()
        assert date(2017, 1, 1) in portfolio_over_time.keys()
        assert date(2017, 1, 2) in portfolio_over_time.keys()
        assert date(2017, 1, 3) not in portfolio_over_time.keys()

    def test_inspect__date_offset(self):
        """
        Tests: Evaluator#inspect_over_time

        Flavour: Test with an date offset
        """
        data = StockData([(date(2017, 1, 1), 150.0), (date(2017, 1, 2), 200.0), (date(2017, 1, 3), 250.0)])
        stock_market_data = StockMarketData({CompanyEnum.COMPANY_A: data})

        portfolio = Portfolio(20000, [SharesOfCompany(CompanyEnum.COMPANY_A, 200)])

        evaluator = PortfolioEvaluator([SimpleTrader(RandomPredictor(), RandomPredictor())])

        portfolio_over_time: dict = \
            evaluator.inspect_over_time(stock_market_data, [portfolio], date_offset=date(2017, 1, 2))['nameless']

        assert date(2016, 12, 31) not in portfolio_over_time.keys()
        assert date(2017, 1, 1) in portfolio_over_time.keys()
        assert date(2017, 1, 2) in portfolio_over_time.keys()
        assert date(2017, 1, 3) not in portfolio_over_time.keys()


class UtilsTest(unittest.TestCase):
    def test_read_stock_market_data(self):
        """
        Tests: evaluator_utils.py/read_stock_market_data

        Read "../datasets/stock_[a|b]_[1962-2011|2012-2015].csv" and check if that happens correctly
        """
        stock_market_data = read_stock_market_data([CompanyEnum.COMPANY_A, CompanyEnum.COMPANY_B],
                                                   [PERIOD_1, PERIOD_2])

        assert stock_market_data.get_number_of_companies() > 0
        assert CompanyEnum.COMPANY_A in stock_market_data.get_companies()
        assert CompanyEnum.COMPANY_B in stock_market_data.get_companies()

    def test_read_stock_market_data__ignore_missing_file(self):
        """
        Tests: evaluator_utils.py/read_stock_market_data

        Read "../datasets/stock_[a|b]_[1962-2011|this-file-does-not-exist].csv" and check if that happens correctly,
         e.g. ignore that one file does not exist
        """
        stock_market_data = read_stock_market_data([CompanyEnum.COMPANY_A, CompanyEnum.COMPANY_B],
                                                   [PERIOD_1, "this-file-does-not-exist"])

        assert stock_market_data.get_number_of_companies() > 0
        assert CompanyEnum.COMPANY_A in stock_market_data.get_companies()
        assert CompanyEnum.COMPANY_B in stock_market_data.get_companies()

    def test_read_stock_market_data__2stocks_2periods(self):
        test = read_stock_market_data([CompanyEnum.COMPANY_A, CompanyEnum.COMPANY_B], [PERIOD_1, PERIOD_2])

        assert test.get_number_of_companies() == 2
        assert CompanyEnum.COMPANY_A in test.get_companies()
        assert CompanyEnum.COMPANY_B in test.get_companies()

    def test_read_stock_market_data__2stocks_1period(self):
        test = read_stock_market_data([CompanyEnum.COMPANY_A, CompanyEnum.COMPANY_B], [PERIOD_1])

        assert test.get_number_of_companies() == 2
        assert CompanyEnum.COMPANY_A in test.get_companies()
        assert CompanyEnum.COMPANY_B in test.get_companies()

    def test_read_stock_market_data__2stocks_no_periods(self):
        test = read_stock_market_data([CompanyEnum.COMPANY_A, CompanyEnum.COMPANY_B], [])

        assert test.get_number_of_companies() == 2
        assert CompanyEnum.COMPANY_A in test.get_companies()
        assert CompanyEnum.COMPANY_B in test.get_companies()

    def test_read_stock_market_data__1stock_2periods(self):
        test = read_stock_market_data([CompanyEnum.COMPANY_B], [PERIOD_1, PERIOD_2])

        assert test.get_number_of_companies() == 1
        assert CompanyEnum.COMPANY_A not in test.get_companies()
        assert CompanyEnum.COMPANY_B in test.get_companies()

    def test_read_stock_market_data__1stock_no_periods(self):
        test = read_stock_market_data([CompanyEnum.COMPANY_B], [])

        assert test.get_number_of_companies() == 1
        assert CompanyEnum.COMPANY_A not in test.get_companies()
        assert CompanyEnum.COMPANY_B in test.get_companies()
