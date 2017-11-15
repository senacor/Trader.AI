'''
Created on 08.11.2017

Module for testing of all trader components

@author: jtymoszuk
'''
import unittest
import evaluating.evaluator

from trading.trader_interface import StockMarketData, Portfolio
from trading.trader_interface import SharesOfCompany
from trading.trader_interface import ITrader
from trading.trader_interface import TradingActionList
from trading.trader_interface import TradingActionEnum
from trading.trader_interface import CompanyEnum
from depenedency_injection_containers import Traders

from datetime import date

import numpy as np
from  definitions import DATASETS_DIR
from evaluating.evaluator import read_stock_market_data


class TraderTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass
   
    def testStockMarketDataConstruction(self):
        companyName2DateValueArrayDict = dict()
        
        today = date(2017, 11, 8)
        yesterday = date(2017, 11, 8)
        date_value_array_1 = np.array([[today, yesterday], [10.0, 20.0]])
        companyName2DateValueArrayDict[CompanyEnum.COMPANY_A.value] = date_value_array_1
        
        date_value_array_2 = np.array([[today, yesterday], [1.0, 2.0]])
        companyName2DateValueArrayDict[CompanyEnum.COMPANY_B.value] = date_value_array_2
        
        stock_market_data = StockMarketData(companyName2DateValueArrayDict)
        stock_market_data.market_data.items()

    def testRandomTraderConstruction(self):
        rt = Traders.random_trader()      
        self.assertTrue(isinstance(rt, ITrader))
        
    def testRandomTrader(self):
        rt = Traders.random_trader()     
        
        shares_of_company_list = list()
        shares_of_company_x = SharesOfCompany(CompanyEnum.COMPANY_A.value, 10)
        shares_of_company_y = SharesOfCompany(CompanyEnum.COMPANY_B.value, 50)
        shares_of_company_list.append(shares_of_company_x)
        shares_of_company_list.append(shares_of_company_y)
        
        portfolio = Portfolio(1000.0, shares_of_company_list)   
        current_portfolio_value = 0.0 #Dummy value
        
        trading_action_list = rt.doTrade(portfolio, current_portfolio_value, read_stock_market_data([[CompanyEnum.COMPANY_A.value,'AAPL']], DATASETS_DIR))
        self.assertTrue(isinstance(trading_action_list, TradingActionList))
        
        self.assertEqual(trading_action_list.len(), 1)
        self.assertEqual(trading_action_list.get(0).action, TradingActionEnum.BUY)
        self.assertEqual(trading_action_list.get(0).shares.amount, 10)
        self.assertEqual(trading_action_list.get(0).shares.name, CompanyEnum.COMPANY_A.value)
        
    def testSimpleTrader(self):
        
        st = Traders.simple_trader_for_test()
        
        shares_of_company_list = list()
        shares_of_company_x = SharesOfCompany(CompanyEnum.COMPANY_A.value, 10)
        shares_of_company_y = SharesOfCompany(CompanyEnum.COMPANY_B.value, 50)
        shares_of_company_list.append(shares_of_company_x)
        shares_of_company_list.append(shares_of_company_y)
        
        portfolio = Portfolio(1000.0, shares_of_company_list)   
        current_portfolio_value = 0.0 #Dummy value
        
        trading_action_list = st.doTrade(portfolio, current_portfolio_value, read_stock_market_data([[CompanyEnum.COMPANY_A.value, 'AAPL']], DATASETS_DIR))
        self.assertTrue(isinstance(trading_action_list, TradingActionList))
        
        self.assertEqual(trading_action_list.len(), 1)
        if(trading_action_list.get(0).action == TradingActionEnum.BUY):
            self.assertEqual(trading_action_list.get(0).action, TradingActionEnum.BUY)
            self.assertEqual(trading_action_list.get(0).shares.amount, 5)
            self.assertEqual(trading_action_list.get(0).shares.name, CompanyEnum.COMPANY_A.value)
        elif (trading_action_list.get(0).action, TradingActionEnum.SELL):
            self.assertEqual(trading_action_list.get(0).action, TradingActionEnum.SELL)
            self.assertEqual(trading_action_list.get(0).shares.amount, 10)
            self.assertEqual(trading_action_list.get(0).shares.name, CompanyEnum.COMPANY_A.value)
        
    def testSimpleTraderConstruction(self):
        st = Traders.simple_trader_for_test()
        self.assertTrue(isinstance(st, ITrader))
        
    def testPortfolioConstruction(self):        
        shares_of_company_list = list()
        shares_of_company_a = SharesOfCompany(CompanyEnum.COMPANY_A.value, 10)
        shares_of_company_b = SharesOfCompany(CompanyEnum.COMPANY_B.value, 50)
        shares_of_company_list.append(shares_of_company_a)
        shares_of_company_list.append(shares_of_company_b)
        
        portfolio = Portfolio(1000.0, shares_of_company_list)
       
        self.assertEqual(portfolio.cash, 1000.0)
        self.assertEqual(len(portfolio.shares), 2)
        self.assertEqual(portfolio.shares[0].name, CompanyEnum.COMPANY_A.value)
        self.assertEqual(portfolio.shares[0].amount, 10)
        
        self.assertEqual(portfolio.shares[1].name, CompanyEnum.COMPANY_B.value)
        self.assertEqual(portfolio.shares[1].amount, 50)

    def testRnnTraderConstruction(self):
        trader = Traders.rnn_trader_with_simple_predictors()
        self.assertTrue(isinstance(trader, ITrader))

    def testRnnTraderGetAction(self):
        trader = Traders.rnn_trader_with_simple_predictors()
        from trading.rnn_trader import State
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
        trader = Traders.rnn_trader_with_simple_predictors()
        self.assertEqual(trader.get_actions_from_index(0), (+1.0, +1.0))
        self.assertEqual(trader.get_actions_from_index(1), (+1.0, +0.5))
        self.assertEqual(trader.get_actions_from_index(2), (+1.0,  0.0))
        self.assertEqual(trader.get_actions_from_index(3), (+1.0, -0.5))
        self.assertEqual(trader.get_actions_from_index(4), (+1.0, -1.0))
        self.assertEqual(trader.get_actions_from_index(5), (+0.5, +1.0))
        self.assertEqual(trader.get_actions_from_index(6), (+0.5, +0.5))
        self.assertEqual(trader.get_actions_from_index(7), (+0.5,  0.0))
        self.assertEqual(trader.get_actions_from_index(8), (+0.5, -0.5))
        self.assertEqual(trader.get_actions_from_index(9), (+0.5, -1.0))
        self.assertEqual(trader.get_actions_from_index(10), (0.0, +1.0))
        self.assertEqual(trader.get_actions_from_index(11), (0.0, +0.5))
        self.assertEqual(trader.get_actions_from_index(12), (0.0,  0.0))
        self.assertEqual(trader.get_actions_from_index(13), (0.0, -0.5))
        self.assertEqual(trader.get_actions_from_index(14), (0.0, -1.0))

    def testGet_index_from_actions(self):
        trader = Traders.rnn_trader_with_simple_predictors()
        self.assertEqual(trader.get_index_from_actions(+1.0, +1.0), 0)
        self.assertEqual(trader.get_index_from_actions(+1.0, +0.5), 1)
        self.assertEqual(trader.get_index_from_actions(+1.0,  0.0), 2)
        self.assertEqual(trader.get_index_from_actions(+1.0, -0.5), 3)
        self.assertEqual(trader.get_index_from_actions(+1.0, -1.0), 4)
        self.assertEqual(trader.get_index_from_actions(+0.5, +1.0), 5)
        self.assertEqual(trader.get_index_from_actions(+0.5, +0.5), 6)
        self.assertEqual(trader.get_index_from_actions(+0.5,  0.0), 7)
        self.assertEqual(trader.get_index_from_actions(+0.5, -0.5), 8)
        self.assertEqual(trader.get_index_from_actions(+0.5, -1.0), 9)
        self.assertEqual(trader.get_index_from_actions( 0.0, +1.0), 10)
        self.assertEqual(trader.get_index_from_actions( 0.0, +0.5), 11)
        self.assertEqual(trader.get_index_from_actions( 0.0,  0.0), 12)
        self.assertEqual(trader.get_index_from_actions( 0.0, -0.5), 13)
        self.assertEqual(trader.get_index_from_actions( 0.0, -1.0), 14)

    def testIndexConversion(self):
        trader = Traders.rnn_trader_with_simple_predictors()
        for index in range(25):
            actionA, actionB = trader.get_actions_from_index(index)
            self.assertEqual(trader.get_index_from_actions(actionA, actionB), index)

    def testActionConversion(self):
        from trading.rnn_trader import STOCKACTIONS
        trader = Traders.rnn_trader_with_simple_predictors()
        for actionA in STOCKACTIONS:
            for actionB in STOCKACTIONS:
                index = trader.get_index_from_actions(actionA, actionB)
                self.assertEqual(trader.get_actions_from_index(index), (actionA, actionB))

    def testRnnTraderDecreaseEpsilon(self):
        trader = Traders.rnn_trader_with_simple_predictors()
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
