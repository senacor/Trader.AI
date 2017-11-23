"""
Created on 19.11.2017

Module for testing of BuyAndHoldTrader.

@author: rmueller
"""
from unittest import TestCase
from model.Portfolio import Portfolio
from model.Order import CompanyEnum, OrderType
from utils import read_stock_market_data
from definitions import PERIOD_1
from trading.trader.reference.buy_and_hold_trader import BuyAndHoldTrader


class BuyAndHoldTraderTest(TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testBuyAndHoldTraderWithOneStock(self):
        trader = BuyAndHoldTrader()
        self.assertIsNotNone(trader)
        stock_market_data = read_stock_market_data([CompanyEnum.COMPANY_A], [PERIOD_1])
        self.assertIsNotNone(stock_market_data)
        portfolio = Portfolio(10000, [])
        self.assertIsNotNone(portfolio)

        # Buy stocks if you haven't bought stocks:
        # With 10000, we can buy 287 stocks A for 34.80 each
        self.assertFalse(trader.bought_stocks)
        order_list = trader.doTrade(portfolio, 0.0, stock_market_data)

        self.assertIsNotNone(order_list)
        self.assertEqual(len(order_list), 1)

        order = order_list[0]
        self.assertEqual(order.action, OrderType.BUY)
        self.assertEqual(order.shares.amount, 287)
        self.assertEqual(order.shares.company_enum, CompanyEnum.COMPANY_A)

        # Don't buy stocks if you have already bought stocks
        self.assertTrue(trader.bought_stocks)
        order_list = trader.doTrade(portfolio, 0.0, stock_market_data)
        self.assertIsNotNone(order_list)
        self.assertEqual(len(order_list), 0)

    def testBuyAndHoldTraderWithTwoStocks(self):
        trader = BuyAndHoldTrader()
        self.assertIsNotNone(trader)
        stock_market_data = read_stock_market_data([CompanyEnum.COMPANY_A, CompanyEnum.COMPANY_B], [PERIOD_1])
        self.assertIsNotNone(stock_market_data)
        portfolio = Portfolio(10000, [])
        self.assertIsNotNone(portfolio)

        # Buy stocks if you haven't bought stocks:
        # With 5000, we can buy 143 stocks A for 34.80 each, and
        # with the remaining 5000, we can buy 31 stocks B for 157.07 each
        self.assertFalse(trader.bought_stocks)
        order_list = trader.doTrade(portfolio, 0.0, stock_market_data)

        self.assertIsNotNone(order_list)
        self.assertEqual(len(order_list), 2)

        order_1 = order_list[0]
        order_2 = order_list[1]

        self.assertEqual(order_1.action, OrderType.BUY)
        self.assertEqual(order_1.shares.amount, 143)
        self.assertEqual(order_1.shares.company_enum, CompanyEnum.COMPANY_A)

        self.assertEqual(order_2.action, OrderType.BUY)
        self.assertEqual(order_2.shares.amount, 31)
        self.assertEqual(order_2.shares.company_enum, CompanyEnum.COMPANY_B)

        # Don't buy stocks if you have already bought stocks
        self.assertTrue(trader.bought_stocks)
        order_list = trader.doTrade(portfolio, 0.0, stock_market_data)
        self.assertIsNotNone(order_list)
        self.assertEqual(len(order_list), 0)
