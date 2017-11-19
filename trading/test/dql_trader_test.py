'''
Created on 19.11.2017

Module for testing of deep q-learning trader.

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
from utils import read_stock_market_data
from trading.trader.dql_trader import State, STOCKACTIONS

class DqlTraderTest(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testRnnTraderGetAction(self):
        trader = Traders.DqlTrader_with_random_prediction()

        state = State(1000, 0, 0, 0, 0, 0, 0)
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
        trader = Traders.DqlTrader_with_random_prediction()
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
        trader = Traders.DqlTrader_with_random_prediction()
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
        trader = Traders.DqlTrader_with_random_prediction()
        for index in range(25):
            actionA, actionB = trader.get_actions_from_index(index)
            self.assertEqual(trader.get_index_from_actions(actionA, actionB), index)

    def testActionConversion(self):
        trader = Traders.DqlTrader_with_random_prediction()
        for actionA in STOCKACTIONS:
            for actionB in STOCKACTIONS:
                index = trader.get_index_from_actions(actionA, actionB)
                self.assertEqual(trader.get_actions_from_index(index), (actionA, actionB))

    def testRnnTraderDecreaseEpsilon(self):
        trader = Traders.DqlTrader_with_random_prediction()
        trader.epsilon = 1.0
        trader.epsilon_min = 0.1
        trader.epsilon_decay = 0.9
        for i in range(30):
            old_epsilon = trader.epsilon
            trader.decrease_epsilon()
            new_epsilon = trader.epsilon
            self.assertLessEqual(new_epsilon, old_epsilon)
            self.assertGreaterEqual(new_epsilon, trader.epsilon_min)


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TraderTest)
    unittest.TextTestRunner(verbosity=2).run(suite)
