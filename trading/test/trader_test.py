'''
Created on 08.11.2017

Module for testing of all trader components

@author: jtymoszuk
'''
import unittest
import evaluating.evaluator

from trading.random_trader import RandomTrader
from trading.simple_trader import SimpleTrader
from trading.trader_interface import StockMarketData
from trading.trader_interface import Portfolio
from trading.trader_interface import SharesOfCompany
from trading.trader_interface import ITrader
from trading.trader_interface import TradingActionList
from trading.trader_interface import TradingActionEnum
from trading.trader_interface import CompanyEnum
from predicting.perfect_stock_a_predictor import PerfectStockAPredictor

from datetime import date

import numpy as np


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
        rt = RandomTrader()        
        self.assertTrue(isinstance(rt, ITrader))
        
    def testRandomTrader(self):
        rt = RandomTrader()     
        
        sharesOfCompanyList = list()
        sharesOfCompanyX = SharesOfCompany(CompanyEnum.COMPANY_A.value, 10)
        sharesOfCompanyY = SharesOfCompany(CompanyEnum.COMPANY_B.value, 50)
        sharesOfCompanyList.append(sharesOfCompanyX)
        sharesOfCompanyList.append(sharesOfCompanyY)
        
        portfolio = Portfolio(1000.0, sharesOfCompanyList)   
        
        tradingActionList = rt.doTrade(portfolio, evaluating.evaluator.read_stock_market_data([CompanyEnum.COMPANY_A.value], '../../datasets/'))
        self.assertTrue(isinstance(tradingActionList, TradingActionList))
        
        self.assertEqual(tradingActionList.len(), 1)
        self.assertEqual(tradingActionList.get(0).action, TradingActionEnum.BUY)
        self.assertEqual(tradingActionList.get(0).shares.amount, 10)
        self.assertEqual(tradingActionList.get(0).shares.name, CompanyEnum.COMPANY_A.value)
        
    def testSimpleTrader(self):
        
        st = SimpleTrader(PerfectStockAPredictor(), None)     
        
        sharesOfCompanyList = list()
        sharesOfCompanyX = SharesOfCompany(CompanyEnum.COMPANY_A.value, 10)
        sharesOfCompanyY = SharesOfCompany(CompanyEnum.COMPANY_B.value, 50)
        sharesOfCompanyList.append(sharesOfCompanyX)
        sharesOfCompanyList.append(sharesOfCompanyY)
        
        portfolio = Portfolio(1000.0, sharesOfCompanyList)   
        
        tradingActionList = st.doTrade(portfolio, evaluating.evaluator.read_stock_market_data([CompanyEnum.COMPANY_A.value], '../../datasets/'))
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
        st = SimpleTrader(PerfectStockAPredictor(), None)
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

    
if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TraderTest)
    unittest.TextTestRunner(verbosity=2).run(suite)
