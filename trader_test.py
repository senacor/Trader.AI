'''
Created on 08.11.2017

Module for testing of all trader components

@author: jtymoszuk
'''
import unittest
from random_trader import RandomTrader
from simple_trader import SimpleTrader
from trader_interface import StockMarketData
from trader_interface import Portfolio
from trader_interface import SharesOfCompany
from trader_interface import ITrader
from trader_interface import TradingAction
from trader_interface import TradingActionEnum


class RandomTraderTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass
    
    def testStockMarketDataConstruction(self):
        StockMarketData()

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
        
        stockMarketData = StockMarketData()

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
