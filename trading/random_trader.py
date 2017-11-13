'''
Created on 08.11.2017

@author: jtymoszuk
'''
from trading.trader_interface import ITrader, TradingActionList
from trading.trader_interface import TradingAction
from trading.trader_interface import StockMarketData
from trading.trader_interface import Portfolio
from trading.trader_interface import TradingActionEnum
from trading.trader_interface import SharesOfCompany
from trading.trader_interface import CompanyEnum


class RandomTrader(ITrader):
    '''
    Random Trader is an implementation of ITrader: doTrade generates TradingAction without any consideration of input data
    '''

    def __init__(self):
        '''
        Constructor
        '''
        
    def doTrade(self, portfolio: Portfolio, stockMarketData: StockMarketData) -> TradingActionList:
        """ Generate action to be taken on the "stock market"
    
        Args:
          portfolio : current Portfolio of this trader_interface
          stockMarketData : StockMarketData for evaluation
        Returns:
          An TradingAction instance
        """
        sharesOfCompany = SharesOfCompany(CompanyEnum.COMPANY_A.value, 10);
        
        result = TradingActionList()
        result.addTradingAction(TradingAction(TradingActionEnum.BUY, sharesOfCompany))
        
        return result
