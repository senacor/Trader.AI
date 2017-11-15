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
        dateValueArray1 = np.array([[today, yesterday], [10.0, 20.0]])
        companyName2DateValueArrayDict[CompanyEnum.COMPANY_A.value] = dateValueArray1
        
        dateValueArray2 = np.array([[today, yesterday], [1.0, 2.0]])
        companyName2DateValueArrayDict[CompanyEnum.COMPANY_B.value] = dateValueArray2
        
        stockMarketData = StockMarketData(companyName2DateValueArrayDict)
        stockMarketData.market_data.items()

    def testRandomTraderConstruction(self):
        rt = Traders.randomTrader()      
        self.assertTrue(isinstance(rt, ITrader))
        
    def testRandomTrader(self):
        rt = Traders.randomTrader()     
        
        sharesOfCompanyList = list()
        sharesOfCompanyX = SharesOfCompany(CompanyEnum.COMPANY_A.value, 10)
        sharesOfCompanyY = SharesOfCompany(CompanyEnum.COMPANY_B.value, 50)
        sharesOfCompanyList.append(sharesOfCompanyX)
        sharesOfCompanyList.append(sharesOfCompanyY)
        
        portfolio = Portfolio(1000.0, sharesOfCompanyList)   
        currentPortfolioValue = 0.0 #Dummy value
        
        tradingActionList = rt.doTrade(portfolio, currentPortfolioValue, read_stock_market_data([[CompanyEnum.COMPANY_A.value,'AAPL']], DATASETS_DIR))
        self.assertTrue(isinstance(tradingActionList, TradingActionList))
        
        self.assertEqual(tradingActionList.len(), 1)
        self.assertEqual(tradingActionList.get(0).action, TradingActionEnum.BUY)
        self.assertEqual(tradingActionList.get(0).shares.amount, 10)
        self.assertEqual(tradingActionList.get(0).shares.name, CompanyEnum.COMPANY_A.value)
        
    def testSimpleTrader(self):
        
        st = Traders.simpleTraderForTest()
        
        sharesOfCompanyList = list()
        sharesOfCompanyX = SharesOfCompany(CompanyEnum.COMPANY_A.value, 10)
        sharesOfCompanyY = SharesOfCompany(CompanyEnum.COMPANY_B.value, 50)
        sharesOfCompanyList.append(sharesOfCompanyX)
        sharesOfCompanyList.append(sharesOfCompanyY)
        
        portfolio = Portfolio(1000.0, sharesOfCompanyList)   
        currentPortfolioValue = 0.0 #Dummy value
        
        tradingActionList = st.doTrade(portfolio, currentPortfolioValue, read_stock_market_data([[CompanyEnum.COMPANY_A.value, 'AAPL']], DATASETS_DIR))
        self.assertTrue(isinstance(tradingActionList, TradingActionList))
        
        self.assertEqual(tradingActionList.len(), 1)
        if(tradingActionList.get(0).action == TradingActionEnum.BUY):
            self.assertEqual(tradingActionList.get(0).action, TradingActionEnum.BUY)
            self.assertEqual(tradingActionList.get(0).shares.amount, 5)
            self.assertEqual(tradingActionList.get(0).shares.name, CompanyEnum.COMPANY_A.value)
        elif (tradingActionList.get(0).action, TradingActionEnum.SELL):
            self.assertEqual(tradingActionList.get(0).action, TradingActionEnum.SELL)
            self.assertEqual(tradingActionList.get(0).shares.amount, 10)
            self.assertEqual(tradingActionList.get(0).shares.name, CompanyEnum.COMPANY_A.value)
        
    def testSimpleTraderConstruction(self):
        st = Traders.simpleTraderForTest()
        self.assertTrue(isinstance(st, ITrader))
        
    def testPortfolioConstruction(self):        
        sharesOfCompanyList = list()
        sharesOfCompanyA = SharesOfCompany(CompanyEnum.COMPANY_A.value, 10)
        sharesOfCompanyB = SharesOfCompany(CompanyEnum.COMPANY_B.value, 50)
        sharesOfCompanyList.append(sharesOfCompanyA)
        sharesOfCompanyList.append(sharesOfCompanyB)
        
        portfolio = Portfolio(1000.0, sharesOfCompanyList)
       
        self.assertEqual(portfolio.cash, 1000.0)
        self.assertEqual(len(portfolio.shares), 2)
        self.assertEqual(portfolio.shares[0].name, CompanyEnum.COMPANY_A.value)
        self.assertEqual(portfolio.shares[0].amount, 10)
        
        self.assertEqual(portfolio.shares[1].name, CompanyEnum.COMPANY_B.value)
        self.assertEqual(portfolio.shares[1].amount, 50)

    def testRnnTraderConstruction(self):
        trader = Traders.rnnTraderWithSimplePredictors()
        self.assertTrue(isinstance(trader, ITrader))

    def testRnnTraderGetAction(self):
        trader = Traders.rnnTraderWithSimplePredictors()
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
        trader = Traders.rnnTraderWithSimplePredictors()
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
        trader = Traders.rnnTraderWithSimplePredictors()
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
        trader = Traders.rnnTraderWithSimplePredictors()
        for index in range(25):
            actionA, actionB = trader.get_actions_from_index(index)
            self.assertEqual(trader.get_index_from_actions(actionA, actionB), index)

    def testActionConversion(self):
        from trading.rnn_trader import STOCKACTIONS
        trader = Traders.rnnTraderWithSimplePredictors()
        for actionA in STOCKACTIONS:
            for actionB in STOCKACTIONS:
                index = trader.get_index_from_actions(actionA, actionB)
                self.assertEqual(trader.get_actions_from_index(index), (actionA, actionB))

    def testRnnTraderDecreaseEpsilon(self):
        trader = Traders.rnnTraderWithSimplePredictors()
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
