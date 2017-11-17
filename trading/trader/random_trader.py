'''
Created on 08.11.2017

@author: jtymoszuk
'''
from model.Portfolio import Portfolio
from model.StockMarketData import StockMarketData
from trading.model.ITrader import ITrader
from trading.model.trader_interface import TradingActionList
from trading.model.trader_interface import CompanyEnum


class RandomTrader(ITrader):
    '''
    Random Trader is an implementation of ITrader: doTrade generates TradingAction without any consideration of input data
    '''

    def __init__(self):
        '''
        Constructor
        '''

    def doTrade(self, portfolio: Portfolio, current_portfolio_value: float, stock_market_data: StockMarketData) -> TradingActionList:
        """ Generate action to be taken on the "stock market"
    
        Args:
          portfolio : current Portfolio of this trader
          current_portfolio_value : value of Portfolio at given Momemnt
          stock_market_data : StockMarketData for evaluation
        Returns:
          A TradingActionList instance, may be empty never None
        """
        # TODO das ist nicht random
        result = TradingActionList()
        result.buy(CompanyEnum.COMPANY_A, 10)

        return result
