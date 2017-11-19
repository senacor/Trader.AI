'''
Created on 19.11.2017

Module for testing of deep q-learning trader.

@author: rmueller
'''
import unittest

from utils import read_stock_market_data
from model.SharesOfCompany import SharesOfCompany
from model.Portfolio import Portfolio
from model.trader_actions import CompanyEnum, TradingActionEnum
from trading.trader.dql_trader import DqlTrader, State, STOCKACTIONS
from predicting.predictor.perfect_predictor import PerfectPredictor

class DqlTraderTest(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testDqlTraderConstruction(self):
        trader = DqlTrader(PerfectPredictor(CompanyEnum.COMPANY_A), PerfectPredictor(CompanyEnum.COMPANY_B), False)
        self.assertIsNotNone(trader)

        trader = DqlTrader(PerfectPredictor(CompanyEnum.COMPANY_A), PerfectPredictor(CompanyEnum.COMPANY_B), True)
        self.assertIsNotNone(trader)

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

    def testGet_actions_from_index(self):
        trader = DqlTrader(PerfectPredictor(CompanyEnum.COMPANY_A), PerfectPredictor(CompanyEnum.COMPANY_B), False)
        self.assertIsNotNone(trader)
        self.assertEqual(trader.get_actions_from_index(0), (+1.0, +1.0))
        self.assertEqual(trader.get_actions_from_index(1), (+1.0, +0.5))
        self.assertEqual(trader.get_actions_from_index(2), (+1.0, 0.0))
        self.assertEqual(trader.get_actions_from_index(3), (+1.0, -0.5))
        self.assertEqual(trader.get_actions_from_index(4), (+1.0, -1.0))
        self.assertEqual(trader.get_actions_from_index(5), (+0.5, +1.0))
        self.assertEqual(trader.get_actions_from_index(6), (+0.5, +0.5))
        self.assertEqual(trader.get_actions_from_index(7), (+0.5, 0.0))
        self.assertEqual(trader.get_actions_from_index(8), (+0.5, -0.5))
        self.assertEqual(trader.get_actions_from_index(9), (+0.5, -1.0))
        self.assertEqual(trader.get_actions_from_index(10), (0.0, +1.0))
        self.assertEqual(trader.get_actions_from_index(11), (0.0, +0.5))
        self.assertEqual(trader.get_actions_from_index(12), (0.0, 0.0))
        self.assertEqual(trader.get_actions_from_index(13), (0.0, -0.5))
        self.assertEqual(trader.get_actions_from_index(14), (0.0, -1.0))

    def testGet_index_from_actions(self):
        trader = DqlTrader(PerfectPredictor(CompanyEnum.COMPANY_A), PerfectPredictor(CompanyEnum.COMPANY_B), False)
        self.assertIsNotNone(trader)
        self.assertEqual(trader.get_index_from_actions(+1.0, +1.0), 0)
        self.assertEqual(trader.get_index_from_actions(+1.0, +0.5), 1)
        self.assertEqual(trader.get_index_from_actions(+1.0, 0.0), 2)
        self.assertEqual(trader.get_index_from_actions(+1.0, -0.5), 3)
        self.assertEqual(trader.get_index_from_actions(+1.0, -1.0), 4)
        self.assertEqual(trader.get_index_from_actions(+0.5, +1.0), 5)
        self.assertEqual(trader.get_index_from_actions(+0.5, +0.5), 6)
        self.assertEqual(trader.get_index_from_actions(+0.5, 0.0), 7)
        self.assertEqual(trader.get_index_from_actions(+0.5, -0.5), 8)
        self.assertEqual(trader.get_index_from_actions(+0.5, -1.0), 9)
        self.assertEqual(trader.get_index_from_actions(0.0, +1.0), 10)
        self.assertEqual(trader.get_index_from_actions(0.0, +0.5), 11)
        self.assertEqual(trader.get_index_from_actions(0.0, 0.0), 12)
        self.assertEqual(trader.get_index_from_actions(0.0, -0.5), 13)
        self.assertEqual(trader.get_index_from_actions(0.0, -1.0), 14)

    def testIndexConversion(self):
        trader = DqlTrader(PerfectPredictor(CompanyEnum.COMPANY_A), PerfectPredictor(CompanyEnum.COMPANY_B), False)
        self.assertIsNotNone(trader)
        for index in range(25):
            actionA, actionB = trader.get_actions_from_index(index)
            self.assertEqual(trader.get_index_from_actions(actionA, actionB), index)

    def testActionConversion(self):
        trader = DqlTrader(PerfectPredictor(CompanyEnum.COMPANY_A), PerfectPredictor(CompanyEnum.COMPANY_B), False)
        self.assertIsNotNone(trader)
        for actionA in STOCKACTIONS:
            for actionB in STOCKACTIONS:
                index = trader.get_index_from_actions(actionA, actionB)
                self.assertEqual(trader.get_actions_from_index(index), (actionA, actionB))

    def testCreateActionList(self):
        trader = DqlTrader(PerfectPredictor(CompanyEnum.COMPANY_A), PerfectPredictor(CompanyEnum.COMPANY_B), False)
        self.assertIsNotNone(trader)
        portfolio = Portfolio(10000, [])
        stock_market_data = read_stock_market_data([CompanyEnum.COMPANY_A, CompanyEnum.COMPANY_B], ['2012-2017'])
        self.assertIsNotNone(stock_market_data)

        # Check doing nothing
        action_a, action_b = 0.0, 0.0
        trading_actions = trader.create_trading_actions(action_a, action_b, portfolio, stock_market_data)
        self.assertIsNotNone(trading_actions)
        self.assertTrue(trading_actions.is_empty())

        # Check buying stock
        action_a, action_b = 1.0, 0.5
        trading_actions = trader.create_trading_actions(action_a, action_b, portfolio, stock_market_data)
        self.assertIsNotNone(trading_actions)
        self.assertEqual(trading_actions.get(0).action, TradingActionEnum.BUY)
        self.assertEqual(trading_actions.get(0).shares.company_enum, CompanyEnum.COMPANY_A)
        self.assertEqual(trading_actions.get(0).shares.amount, 98)
        self.assertEqual(trading_actions.get(1).action, TradingActionEnum.BUY)
        self.assertEqual(trading_actions.get(1).shares.company_enum, CompanyEnum.COMPANY_B)
        self.assertEqual(trading_actions.get(1).shares.amount, 33)

        # Check selling stock without enough owned shares
        action_a, action_b = -1.0, -0.5
        trading_actions = trader.create_trading_actions(action_a, action_b, portfolio, stock_market_data)
        self.assertIsNotNone(trading_actions)
        self.assertTrue(trading_actions.is_empty())

        # Check selling stock with enough owned shares
        portfolio = Portfolio(10000, [SharesOfCompany(CompanyEnum.COMPANY_A, 2), SharesOfCompany(CompanyEnum.COMPANY_B, 2)])
        action_a, action_b = -1.0, -0.5
        trading_actions = trader.create_trading_actions(action_a, action_b, portfolio, stock_market_data)
        self.assertIsNotNone(trading_actions)
        self.assertEqual(trading_actions.get(0).action, TradingActionEnum.SELL)
        self.assertEqual(trading_actions.get(0).shares.company_enum, CompanyEnum.COMPANY_A)
        self.assertEqual(trading_actions.get(0).shares.amount, 2)
        self.assertEqual(trading_actions.get(1).action, TradingActionEnum.SELL)
        self.assertEqual(trading_actions.get(1).shares.company_enum, CompanyEnum.COMPANY_B)
        self.assertEqual(trading_actions.get(1).shares.amount, 1)
