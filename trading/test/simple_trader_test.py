'''
Created on 19.11.2017

Module for testing the SimpleTrader.

@author: rmueller
'''
import unittest
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
from predicting.predictor.perfect_predictor import PerfectPredictor
from trading.trader.simple_trader import SimpleTrader
from utils import read_stock_market_data


class SimpleTraderTest(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testSimpleTraderWithOneStock(self):
        trader = SimpleTrader(PerfectPredictor(CompanyEnum.COMPANY_A), PerfectPredictor(CompanyEnum.COMPANY_B))
        self.assertIsNotNone(trader)
        stock_market_data = read_stock_market_data([CompanyEnum.COMPANY_A], ['1962-2011'])
        self.assertIsNotNone(stock_market_data)
        portfolio = Portfolio(10000, [])
        self.assertIsNotNone(portfolio)

        # Buy stocks based on prediction: With 10000, we can buy 287 stocks A for 34.80 each
        trading_action_list = trader.doTrade(portfolio, 0.0, stock_market_data)
        self.assertIsNotNone(trading_action_list)
        self.assertEqual(trading_action_list.len(), 1)
        self.assertEqual(trading_action_list.get(0).action, TradingActionEnum.BUY)
        self.assertEqual(trading_action_list.get(0).shares.amount, 287)
        self.assertEqual(trading_action_list.get(0).shares.company_enum, CompanyEnum.COMPANY_A)

    def testSimpleTraderWithTwoStocks(self):
        trader = SimpleTrader(PerfectPredictor(CompanyEnum.COMPANY_A), PerfectPredictor(CompanyEnum.COMPANY_B))
        self.assertIsNotNone(trader)
        stock_market_data = read_stock_market_data([CompanyEnum.COMPANY_A, CompanyEnum.COMPANY_B], ['1962-2011'])
        self.assertIsNotNone(stock_market_data)
        portfolio = Portfolio(10000, [])
        self.assertIsNotNone(portfolio)

        # Buy stocks based on prediction:
        # SimpleTrader buys only stocks A again
        # TODO @Janusz Why doesn't SimpleTrader buy stocks B?
        # This is because `SimpleTrader` buys sequentially without considering future/earlier trade actions. So in case
        # of two BUY actions, all available cash is spent for buying the first stock - an issue I already raised (jh)
        trading_action_list = trader.doTrade(portfolio, 0.0, stock_market_data)
        self.assertIsNotNone(trading_action_list)
        self.assertEqual(trading_action_list.len(), 1)
        self.assertEqual(trading_action_list.get(0).action, TradingActionEnum.BUY)
        self.assertEqual(trading_action_list.get(0).shares.amount, 287)
        self.assertEqual(trading_action_list.get(0).shares.company_enum, CompanyEnum.COMPANY_A)
