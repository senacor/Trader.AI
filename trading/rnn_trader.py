'''
Created on 13.11.2017

@author: jtymoszuk
'''

from trading.trader_interface import Portfolio
from trading.trader_interface import ITrader
from trading.trader_interface import StockMarketData
from trading.trader_interface import TradingActionList


class RnnTrader(ITrader):
    '''
    Implementation of ITrader based on Reinforced Neural Network (RNN): doTrade generates TradingActionList according to last generated changes on Portfolio value.
    '''

    def __init__(self, params):
        '''
        Constructor
        '''

        def doTrade(self, portfolio: Portfolio, currentPortfolioValue: float, stockMarketData: StockMarketData) -> TradingActionList:
            """ Generate action to be taken on the "stock market"
        
            Args:
              portfolio : current Portfolio of this trader
              currentPortfolioValue : value of Portfolio at given Momemnt
              stockMarketData : StockMarketData for evaluation
              company_a_name : optional name of 1st company, or default
              company_b_name : optional name of 2nd company, or default
            Returns:
              A TradingActionList instance, may be empty never None
            """
            # TODO implement me
            return None   
        
