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
from predicting.perfect_stock_a_predictor import PerfectStockAPredictor


class SimpleTrader(ITrader):
    '''
    Simple Trader generates TradingAction based on simple logic, input data and prediction from NN-Engine
    '''

    def __init__(self):
        '''
        Constructor
        '''
        self.perfectStockAPredictor = PerfectStockAPredictor()
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
        
        predictedNextAppleValue = self.perfectStockAPredictor.doPredict(appleData)
        # predictedNextGoogleValue = self.perfectStockAPredictor.doPredict(googleData)
        
        tradingAction = None
        if predictedNextAppleValue > lastValue:
            tradingAction = TradingActionEnum.BUY
        elif predictedNextAppleValue < lastValue:
            tradingAction = TradingActionEnum.SELL
        
        if tradingAction == TradingActionEnum.BUY:
            if(portfolio.cash > lastValue) :
                # We can buy something
                amountOfUnitsToBuy = int(portfolio.cash // lastValue)
                sharesOfCompany = SharesOfCompany(CompanyEnum.APPLE.value, amountOfUnitsToBuy);
                result = TradingAction(tradingAction, sharesOfCompany)
        elif tradingAction == TradingActionEnum.SELL:
            # Check if something can be selled
            sharesOfAppleInPortfolio = self.findSharesOfCompany(CompanyEnum.APPLE.value, portfolio.shares)
            if(sharesOfAppleInPortfolio is not None) :
                # Sell everything
                sharesOfCompany = SharesOfCompany(CompanyEnum.APPLE.value, sharesOfAppleInPortfolio.amountOfShares);
                result = TradingAction(tradingAction, sharesOfCompany)
            else:
                # Nothing to sell
                result = None
          
        return result
        
    def findSharesOfCompany(self , companyName: str, shares: list) -> SharesOfCompany:
        """ Finds SharesOfCompany in list by company name
    
        Args:
          companyName : company to find
          list : list with SharesOfCompany
        Returns:
          SharesOfCompany for given company or None 
        """
        for sharesOfCompany in shares:
            if (isinstance(sharesOfCompany, SharesOfCompany) and sharesOfCompany.companyName == companyName):
                return sharesOfCompany
        
        return None 
        
