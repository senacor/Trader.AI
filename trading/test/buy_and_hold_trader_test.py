'''
Created on 19.11.2017

Module for testing of BuyAndHoldTrader.

@author: rmueller
'''
from unittest import TestCase
from model.Portfolio import Portfolio
from model.trader_actions import CompanyEnum, TradingActionEnum
from utils import read_stock_market_data
from trading.trader.buy_and_hold_trader import BuyAndHoldTrader
from definitions import PERIOD_1

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
        trading_action_list = trader.doTrade(portfolio, 0.0, stock_market_data)
        self.assertIsNotNone(trading_action_list)
        self.assertEqual(trading_action_list.len(), 1)
        self.assertEqual(trading_action_list.get(0).action, TradingActionEnum.BUY)
        self.assertEqual(trading_action_list.get(0).shares.amount, 287)
        self.assertEqual(trading_action_list.get(0).shares.company_enum, CompanyEnum.COMPANY_A)

        # Don't buy stocks if you have already bought stocks
        self.assertTrue(trader.bought_stocks)
        trading_action_list = trader.doTrade(portfolio, 0.0, stock_market_data)
        self.assertIsNotNone(trading_action_list)
        self.assertEqual(trading_action_list.len(), 0)

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
        trading_action_list = trader.doTrade(portfolio, 0.0, stock_market_data)
        self.assertIsNotNone(trading_action_list)
        self.assertEqual(trading_action_list.len(), 2)
        self.assertEqual(trading_action_list.get(0).action, TradingActionEnum.BUY)
        self.assertEqual(trading_action_list.get(0).shares.amount, 143)
        self.assertEqual(trading_action_list.get(0).shares.company_enum, CompanyEnum.COMPANY_A)
        self.assertEqual(trading_action_list.get(1).action, TradingActionEnum.BUY)
        self.assertEqual(trading_action_list.get(1).shares.amount, 31)
        self.assertEqual(trading_action_list.get(1).shares.company_enum, CompanyEnum.COMPANY_B)

        # Don't buy stocks if you have already bought stocks
        self.assertTrue(trader.bought_stocks)
        trading_action_list = trader.doTrade(portfolio, 0.0, stock_market_data)
        self.assertIsNotNone(trading_action_list)
        self.assertEqual(trading_action_list.len(), 0)
