"""
Created on 19.11.2017

Module for testing the SimpleTrader.

@author: rmueller
"""
import unittest
from model.Portfolio import Portfolio
from model.Order import OrderType
from model.Order import CompanyEnum

from utils import read_stock_market_data
from predicting.predictor.reference.perfect_predictor import PerfectPredictor
from definitions import PERIOD_1
from trading.trader.reference.simple_trader import SimpleTrader


class SimpleTraderTest(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testSimpleTraderWithOneStock(self):
        trader = SimpleTrader(PerfectPredictor(CompanyEnum.COMPANY_A), PerfectPredictor(CompanyEnum.COMPANY_B))
        self.assertIsNotNone(trader)
        stock_market_data = read_stock_market_data([CompanyEnum.COMPANY_A], [PERIOD_1])
        self.assertIsNotNone(stock_market_data)
        portfolio = Portfolio(10000, [])
        self.assertIsNotNone(portfolio)

        # Buy stocks based on prediction: With 10000, we can buy 287 stocks A for 34.80 each
        order_list = trader.doTrade(portfolio, 0.0, stock_market_data)
        self.assertIsNotNone(order_list)

        self.assertEqual(len(order_list), 1)

        order = order_list[0]
        self.assertEqual(order.action, OrderType.BUY)
        self.assertEqual(order.shares.amount, 287)
        self.assertEqual(order.shares.company_enum, CompanyEnum.COMPANY_A)

    def testSimpleTraderWithTwoStocks(self):
        trader = SimpleTrader(PerfectPredictor(CompanyEnum.COMPANY_A), PerfectPredictor(CompanyEnum.COMPANY_B))
        self.assertIsNotNone(trader)
        stock_market_data = read_stock_market_data([CompanyEnum.COMPANY_A, CompanyEnum.COMPANY_B], [PERIOD_1])
        self.assertIsNotNone(stock_market_data)
        portfolio = Portfolio(10000, [])
        self.assertIsNotNone(portfolio)

        # Buy stocks based on prediction:
        # SimpleTrader buys only stocks A again
        # Why doesn't SimpleTrader buy stocks B?
        # This is because `SimpleTrader` buys sequentially without considering future/earlier trade actions. So in case
        # of two BUY actions, all available cash is spent for buying the first stock - an issue I already raised (jh)
        order_list = trader.doTrade(portfolio, 0.0, stock_market_data)

        order_list = order_list
        self.assertIsNotNone(order_list)

        self.assertEqual(len(order_list), 1)

        order = order_list[0]
        self.assertEqual(order.action, OrderType.BUY)
        self.assertEqual(order.shares.amount, 287)
        self.assertEqual(order.shares.company_enum, CompanyEnum.COMPANY_A)
