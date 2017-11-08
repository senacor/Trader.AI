'''
Created on 08.11.2017

@author: jtymoszuk
'''
from trading.trader_interface import ITrader
from trading.trader_interface import TradingAction
from trading.trader_interface import StockMarketData
from trading.trader_interface import Portfolio
from trading.trader_interface import TradingActionEnum
from trading.trader_interface import SharesOfCompany
from trading.trader_interface import CompanyEnum
from predicting.simple_predictor import SimplePredictor


class SimpleTrader(ITrader):
    '''
    Simple Trader generates TradingAction based on simple logic, input data and prediction from NN-Engine
    '''

    def __init__(self):
        '''
        Constructor
        '''
        self.applePredictor = SimplePredictor()
        self.bmwPredictor = SimplePredictor()
        
    def doTrade(self, portfolio: Portfolio, stockMarketData: StockMarketData) -> TradingAction:
        """ Generate action to be taken on the "stock market"
    
        Args:
          portfolio : current Portfolio of this trader_interface
          stockMarketData : StockMarketData for evaluation
        Returns:
          An TradingAction instance
        """
        
        appleData = stockMarketData.companyName2DateValueArrayDict.get(CompanyEnum.APPLE.value)
        lastValue = appleData[-1][-1]
        # googleData =stockMarketData.companyName2DateValueArrayDict.get(CompanyEnum.GOOGLE.value)
        
        predictedNextAppleValue = self.applePredictor.doPredict(appleData)
        # predictedNextGoogleValue = self.applePredictor.doPredict(googleData)
        
        tradingAction = None
        if predictedNextAppleValue > lastValue:
            tradingAction = TradingActionEnum.BUY
        elif predictedNextAppleValue < lastValue:
            tradingAction = TradingActionEnum.SELL
        
        if not (tradingAction is None):
            sharesOfCompany = SharesOfCompany(CompanyEnum.APPLE.value, 10);
            result = TradingAction(tradingAction, sharesOfCompany)
        else:
            result = None
          
        return result
        
