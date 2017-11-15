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

    def doTrade(self, portfolio: Portfolio, current_portfolio_value: float, stock_market_data: StockMarketData) -> TradingActionList:
        """ Generate action to be taken on the "stock market"
    
        Args:
          portfolio : current Portfolio of this trader
          current_portfolio_value : value of Portfolio at given Momemnt
          stock_market_data : StockMarketData for evaluation
        Returns:
          A TradingActionList instance, may be empty never None
        """
        shares_of_company = SharesOfCompany(CompanyEnum.COMPANY_A.value, 10);

        result = TradingActionList()
        result.addTradingAction(TradingAction(TradingActionEnum.BUY, shares_of_company))

        return result
