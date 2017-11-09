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
from predicting.predictor_interface import IPredictor


class SimpleTrader(ITrader):
    '''
    Simple Trader generates TradingAction based on simple logic, input data and prediction from NN-Engine
    '''

    def __init__(self, predictor: IPredictor = None):
        '''
        Constructor
        '''
        if (predictor is not None):
            self.predictor = predictor
        else:
            self.predictor = PerfectStockAPredictor()

    def doTrade(self, portfolio: Portfolio, stockMarketData: StockMarketData) -> TradingAction:
        """ Generate action to be taken on the "stock market"
    
        Args:
          portfolio : current Portfolio of this trader_interface
          stockMarketData : StockMarketData for evaluation
        Returns:
          An TradingAction instance
        """

        symbol = next(iter(stockMarketData.market_data.keys()))
        appleData = stockMarketData.market_data[symbol]
        lastValue = appleData[-1][-1]
        # googleData =stockMarketData.companyName2DateValueArrayDict.get(CompanyEnum.GOOGLE.value)

        predictedNextAppleValue = self.predictor.doPredict(appleData)
        # predictedNextGoogleValue = self.perfectStockAPredictor.doPredict(googleData)

        result = None
        tradingAction = None
        if predictedNextAppleValue > lastValue:
            tradingAction = TradingActionEnum.BUY
        elif predictedNextAppleValue < lastValue:
            tradingAction = TradingActionEnum.SELL

        if tradingAction == TradingActionEnum.BUY:
            if (portfolio.cash > lastValue):
                # We can buy something
                amountOfUnitsToBuy = int(portfolio.cash // lastValue)
                sharesOfCompany = SharesOfCompany(symbol, amountOfUnitsToBuy);
                result = TradingAction(tradingAction, sharesOfCompany)
        elif tradingAction == TradingActionEnum.SELL:
            # Check if something can be selled
            sharesOfAppleInPortfolio = self.findSharesOfCompany(symbol, portfolio.shares)
            if (sharesOfAppleInPortfolio is not None):
                # Sell everything
                sharesOfCompany = SharesOfCompany(symbol, sharesOfAppleInPortfolio.amount);
                result = TradingAction(tradingAction, sharesOfCompany)
            else:
                # Nothing to sell
                result = None

        return result

    def findSharesOfCompany(self, companyName: str, shares: list) -> SharesOfCompany:
        """ Finds SharesOfCompany in list by company name
    
        Args:
          companyName : company to find
          list : list with SharesOfCompany
        Returns:
          SharesOfCompany for given company or None 
        """
        for sharesOfCompany in shares:
            if (isinstance(sharesOfCompany, SharesOfCompany) and sharesOfCompany.name == companyName):
                return sharesOfCompany

        return None
