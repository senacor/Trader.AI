'''
Created on 08.11.2017

@author: jtymoszuk
'''
from trader_interface import ITrader
from trader_interface import TradingAction
from trader_interface import StockMarketData
from trader_interface import Portfolio
from trader_interface import TradingActionEnum
from trader_interface import SharesOfCompany


class RandomTrader(ITrader):
    '''
    Random Trader is an implementation of ITrader: doTrade generates TradingAction without any consideration of input data
    '''

    def __init__(self):
        '''
        Constructor
        '''
        
    def doTrade(self, portfolio: Portfolio, stockMarketData: StockMarketData) -> TradingAction:
        """ Generate action to be taken on the "stock market"
    
        Args:
          portfolio : current Portfolio of this trader_interface
          stockMarketData : StockMarketData for evaluation
        Returns:
          An TradingAction instance
        """
        sharesOfCompany = SharesOfCompany("Postbank", 10);
        
        result = TradingAction(TradingActionEnum.BUY, sharesOfCompany)
        
        return result
        
