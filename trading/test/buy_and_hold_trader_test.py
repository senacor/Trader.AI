'''
Created on 19.11.2017

Module for testing of BuyAndHoldTrader.

@author: rmueller
'''
from unittest import TestCase
from model.Portfolio import Portfolio
from model.StockMarketData import StockMarketData
from model.ITrader import ITrader

from model.trader_actions import SharesOfCompany
from model.trader_actions import TradingActionList
from model.trader_actions import TradingActionEnum
from model.trader_actions import CompanyEnum
from dependency_injection_containers import Traders

from datetime import date

import numpy as np
from  definitions import DATASETS_DIR
from trading.trader.buy_and_hold_trader import BuyAndHoldTrader
from utils import read_stock_market_data


class BuyAndHoldTraderTest(TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testBuyAndHoldTraderForOneStock(self):
        trader = BuyAndHoldTrader()
        self.assertIsNotNone(trader)
        stock_market_data = read_stock_market_data([CompanyEnum.COMPANY_A], ['1962-2011'])
        self.assertIsNotNone(stock_market_data)
        portfolio = Portfolio(10000, [])
        self.assertIsNotNone(portfolio)

        # Buy stocks if you haven't bought stocks
        self.assertFalse(trader.bought_stocks)
        trading_action_list = trader.doTrade(portfolio, 0.0, stock_market_data)
        self.assertIsNotNone(trading_action_list)
        self.assertEqual(trading_action_list.len(), 1)

        # Don't buy stocks if you have already bought stocks
        self.assertTrue(trader.bought_stocks)
        trading_action_list = trader.doTrade(portfolio, 0.0, stock_market_data)
        self.assertIsNotNone(trading_action_list)
        self.assertEqual(trading_action_list.len(), 0)

    def testBuyAndHoldTraderForTwoStocks(self):
        trader = BuyAndHoldTrader()
        self.assertIsNotNone(trader)
        stock_market_data = read_stock_market_data([CompanyEnum.COMPANY_A, CompanyEnum.COMPANY_B], ['1962-2011'])
        self.assertIsNotNone(stock_market_data)
        portfolio = Portfolio(10000, [])
        self.assertIsNotNone(portfolio)

        # Buy stocks if you haven't bought stocks
        self.assertFalse(trader.bought_stocks)
        trading_action_list = trader.doTrade(portfolio, 0.0, stock_market_data)
        self.assertIsNotNone(trading_action_list)
        self.assertEqual(trading_action_list.len(), 2)

        # Don't buy stocks if you have already bought stocks
        self.assertTrue(trader.bought_stocks)
        trading_action_list = trader.doTrade(portfolio, 0.0, stock_market_data)
        self.assertIsNotNone(trading_action_list)
        self.assertEqual(trading_action_list.len(), 0)
