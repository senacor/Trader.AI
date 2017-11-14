'''
Created on 08.11.2017

@author: jtymoszuk
'''
from trading.trader_interface import ITrader, TradingActionList, Portfolio
from trading.trader_interface import TradingAction
from trading.trader_interface import StockMarketData
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
        sharesOfCompany = SharesOfCompany(CompanyEnum.COMPANY_A.value, 10);

        result = TradingActionList()
        result.addTradingAction(TradingAction(TradingActionEnum.BUY, sharesOfCompany))

        return result
