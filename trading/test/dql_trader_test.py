'''
Created on 19.11.2017

Module for testing of deep q-learning trader.

@author: rmueller
'''
import unittest

from definitions import PERIOD_3
from utils import read_stock_market_data
from model.SharesOfCompany import SharesOfCompany
from model.Portfolio import Portfolio
from model.trader_actions import CompanyEnum, TradingActionEnum
from trading.trader.dql_trader import DqlTrader, State
from predicting.predictor.reference.perfect_predictor import PerfectPredictor

class DqlTraderTest(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testGetAction(self):
        trader = DqlTrader(PerfectPredictor(CompanyEnum.COMPANY_A), PerfectPredictor(CompanyEnum.COMPANY_B), False)
        self.assertIsNotNone(trader)

        state = State(1000, 0, 0, 0, 0, 0, 0)
        self.assertIsNotNone(state)
        # Check random actions because epsilon is 1.0
        trader.epsilon = 1.0
        for i in range(100):
            actionA, actionB = trader.get_action(state)
            self.assertGreaterEqual(actionA, -1.0)
            self.assertGreaterEqual(actionB, -1.0)
            self.assertLessEqual(actionA, 1.0)
            self.assertLessEqual(actionB, 1.0)
        # Check predicted actions because epsilon is 0.0
        trader.epsilon = 0.0
        for i in range(100):
            actionA, actionB = trader.get_action(state)
            self.assertGreaterEqual(actionA, -1.0)
            self.assertGreaterEqual(actionB, -1.0)
            self.assertLessEqual(actionA, 1.0)
            self.assertLessEqual(actionB, 1.0)

    def testCreateActionList(self):
        trader = DqlTrader(PerfectPredictor(CompanyEnum.COMPANY_A), PerfectPredictor(CompanyEnum.COMPANY_B), False)
        self.assertIsNotNone(trader)
        portfolio = Portfolio(10000, [])
        stock_market_data = read_stock_market_data([CompanyEnum.COMPANY_A, CompanyEnum.COMPANY_B], [PERIOD_3])
        self.assertIsNotNone(stock_market_data)

        # Check doing nothing
        # commented because that STOCKACTION is not used anymore
        # action_a, action_b = 0.0, 0.0
        # trading_actions = trader.create_trading_actions(action_a, action_b, portfolio, stock_market_data)
        # self.assertIsNotNone(trading_actions)
        # self.assertTrue(trading_actions.is_empty())

        # Check buying halve stock
        # commented because that STOCKACTION is not used anymore
        # action_a, action_b = 0.5, 0.5
        # trading_actions = trader.create_trading_actions(action_a, action_b, portfolio, stock_market_data)
        # self.assertIsNotNone(trading_actions)
        # self.assertEqual(trading_actions.get(0).action, TradingActionEnum.BUY)
        # self.assertEqual(trading_actions.get(0).shares.company_enum, CompanyEnum.COMPANY_A)
        # self.assertEqual(trading_actions.get(0).shares.amount, 49)
        # self.assertEqual(trading_actions.get(1).action, TradingActionEnum.BUY)
        # self.assertEqual(trading_actions.get(1).shares.company_enum, CompanyEnum.COMPANY_B)
        # self.assertEqual(trading_actions.get(1).shares.amount, 33)

        # Check buying full stock
        action_a, action_b = 1.0, 1.0
        trading_actions = trader.create_trading_actions(action_a, action_b, portfolio, stock_market_data)
        self.assertIsNotNone(trading_actions)
        self.assertEqual(trading_actions.get(0).action, TradingActionEnum.BUY)
        self.assertEqual(trading_actions.get(0).shares.company_enum, CompanyEnum.COMPANY_A)
        self.assertEqual(trading_actions.get(0).shares.amount, 98)
        self.assertEqual(trading_actions.get(1).action, TradingActionEnum.BUY)
        self.assertEqual(trading_actions.get(1).shares.company_enum, CompanyEnum.COMPANY_B)
        self.assertEqual(trading_actions.get(1).shares.amount, 66)

        # Check selling stock without enough owned shares
        action_a, action_b = -1.0, -1.0
        trading_actions = trader.create_trading_actions(action_a, action_b, portfolio, stock_market_data)
        self.assertIsNotNone(trading_actions)
        self.assertTrue(trading_actions.is_empty())

        # Check selling halve stock with enough owned shares
        # commented because that STOCKACTION is not used anymore
        # portfolio = Portfolio(10000, [SharesOfCompany(CompanyEnum.COMPANY_A, 2), SharesOfCompany(CompanyEnum.COMPANY_B, 2)])
        # action_a, action_b = -0.5, -0.5
        # trading_actions = trader.create_trading_actions(action_a, action_b, portfolio, stock_market_data)
        # self.assertIsNotNone(trading_actions)
        # self.assertEqual(trading_actions.get(0).action, TradingActionEnum.SELL)
        # self.assertEqual(trading_actions.get(0).shares.company_enum, CompanyEnum.COMPANY_A)
        # self.assertEqual(trading_actions.get(0).shares.amount, 2)
        # self.assertEqual(trading_actions.get(1).action, TradingActionEnum.SELL)
        # self.assertEqual(trading_actions.get(1).shares.company_enum, CompanyEnum.COMPANY_B)
        # self.assertEqual(trading_actions.get(1).shares.amount, 1)

        # Check selling full stock with enough owned shares
        portfolio = Portfolio(10000, [SharesOfCompany(CompanyEnum.COMPANY_A, 2), SharesOfCompany(CompanyEnum.COMPANY_B, 2)])
        action_a, action_b = -1.0, -1.0
        trading_actions = trader.create_trading_actions(action_a, action_b, portfolio, stock_market_data)
        self.assertIsNotNone(trading_actions)
        self.assertEqual(trading_actions.get(0).action, TradingActionEnum.SELL)
        self.assertEqual(trading_actions.get(0).shares.company_enum, CompanyEnum.COMPANY_A)
        self.assertEqual(trading_actions.get(0).shares.amount, 2)
        self.assertEqual(trading_actions.get(1).action, TradingActionEnum.SELL)
        self.assertEqual(trading_actions.get(1).shares.company_enum, CompanyEnum.COMPANY_B)
        self.assertEqual(trading_actions.get(1).shares.amount, 2)
