'''
Created on 08.11.2017

Module for testing of all trader components

@author: jtymoszuk
'''
import unittest
from trading.random_trader import RandomTrader
from trading.simple_trader import SimpleTrader
from trading.trader_interface import StockMarketData
from trading.trader_interface import Portfolio
from trading.trader_interface import SharesOfCompany
from trading.trader_interface import ITrader
from trading.trader_interface import TradingAction
from trading.trader_interface import TradingActionEnum
from datetime import date

import numpy as np


class RandomTraderTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass
    
    def testStockMarketDataConstruction(self):
        
        companyName2DateValueArrayDict = dict()
        
        today = date(2017, 11, 8)
        yesterday = date(2017, 11, 8)
        dateValueArray1 = np.array([[today, yesterday], [10.0, 20.0]])
        companyName2DateValueArrayDict["Postbank"] = dateValueArray1
        
        dateValueArray2 = np.array([[today, yesterday], [1.0, 2.0]])
        companyName2DateValueArrayDict["BMW"] = dateValueArray2
        
        stockMarketData = StockMarketData(companyName2DateValueArrayDict)
        stockMarketData.companyName2DateValueArrayDict.items()

    def testRandomTraderConstruction(self):
        rt = RandomTrader()        
        self.assertTrue(isinstance(rt, ITrader))
        
    def testRandomTrader(self):
        rt = RandomTrader()     
        
        sharesOfCompanyList = list()
        sharesOfCompanyX = SharesOfCompany("Company X", 10)
        sharesOfCompanyY = SharesOfCompany("Company Y", 50)
        sharesOfCompanyList.append(sharesOfCompanyX)
        sharesOfCompanyList.append(sharesOfCompanyY)
        
        portfolio = Portfolio(1000.0, sharesOfCompanyList)   
        
        companyName2DateValueArrayDict = dict()
        
        today = date(2017, 11, 8)
        yesterday = date(2017, 11, 8)
        dateValueArray = np.array([[today, yesterday], [10.0, 20.0]])
        companyName2DateValueArrayDict["Postbank"] = dateValueArray
        stockMarketData = StockMarketData(companyName2DateValueArrayDict)

        tradingAction = rt.doTrade(portfolio, stockMarketData)
        self.assertTrue(isinstance(tradingAction, TradingAction))
        
        self.assertEqual(tradingAction.actionEnum, TradingActionEnum.BUY)
        self.assertEqual(tradingAction.sharesOfCompany.amountOfShares, 10)
        self.assertEqual(tradingAction.sharesOfCompany.companyName, "Postbank")
        
    def testSimpleTraderConstruction(self):
        st = SimpleTrader()
        self.assertTrue(isinstance(st, ITrader))
        
    def testPortfolioConstruction(self):        
        sharesOfCompanyList = list()
        sharesOfCompanyX = SharesOfCompany("Company X", 10)
        sharesOfCompanyY = SharesOfCompany("Company Y", 50)
        sharesOfCompanyList.append(sharesOfCompanyX)
        sharesOfCompanyList.append(sharesOfCompanyY)
        
        portfolio = Portfolio(1000.0, sharesOfCompanyList)
       
        self.assertEqual(portfolio.cash, 1000.0)
        self.assertEqual(len(portfolio.shares), 2)
        self.assertEqual(portfolio.shares[0].companyName, "Company X")
        self.assertEqual(portfolio.shares[0].amountOfShares, 10)
        
        self.assertEqual(portfolio.shares[1].companyName, "Company Y")
        self.assertEqual(portfolio.shares[1].amountOfShares, 50)

    
if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(RandomTraderTest)
    unittest.TextTestRunner(verbosity=2).run(suite)
