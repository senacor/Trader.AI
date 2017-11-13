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
from predicting.predictor_interface import IPredictor
import copy


class SimpleTrader(ITrader):
    '''
    Simple Trader generates TradingAction based on simple logic, input data and prediction from NN-Engine
    '''

    def __init__(self, stockAPredictor: IPredictor, stockBPredictor: IPredictor):
        '''
        Constructor
        '''
        self.stockAPredictor = stockAPredictor
        self.stockBPredictor = stockBPredictor

    def doTrade(self, portfolio: Portfolio, currentPortfolioValue: float, stockMarketData: StockMarketData,
                company_a_name=CompanyEnum.COMPANY_A.value,
                company_b_name=CompanyEnum.COMPANY_B.value) -> TradingActionList:
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
        
        localPortfolio = copy.deepcopy(portfolio)
        
        result = TradingActionList()

        companyAName = company_a_name
        companyAData = stockMarketData.market_data.get(companyAName)
        if (self.stockAPredictor is not None and companyAData is not None):
            self.tradeForCompany(companyAName, companyAData, self.stockAPredictor, localPortfolio, result)
        else:
            # TODO: use Logging!!!
            print("!!!! SimpleTrader: stockAPredictor or companyAData is None -> No prediction for Company A")

        companyBName = company_b_name
        companyBData = stockMarketData.market_data.get(companyBName)
        if (self.stockBPredictor is not None and companyBData is not None):
            self.tradeForCompany(companyBName, companyBData, self.stockBPredictor, localPortfolio, result)
        else:
            # TODO: use Logging!!!
            print("!!!! SimpleTrader: stockBPredictor or companyBData is None -> No prediction for Company B")

        return result

    def tradeForCompany(self, companyName: str, companyData: list, predictor: IPredictor, portfolio: Portfolio,
                        resultTradingActionList: TradingActionList):

        lastValue = companyData[-1][-1]
        predictedNextAppleValue = predictor.doPredict(companyData)

        tradingAction = None
        if predictedNextAppleValue > lastValue:
            tradingAction = TradingActionEnum.BUY
        elif predictedNextAppleValue < lastValue:
            tradingAction = TradingActionEnum.SELL

        if tradingAction == TradingActionEnum.BUY:
            if (portfolio.cash > lastValue):
                # We can buy something
                amountOfUnitsToBuy = int(portfolio.cash // lastValue)
                sharesOfCompany = SharesOfCompany(companyName, amountOfUnitsToBuy);
                resultTradingActionList.addTradingAction(TradingAction(tradingAction, sharesOfCompany))
                
                #Update Cash in portfolio
                portfolio.cash = portfolio.cash - (amountOfUnitsToBuy * lastValue)
                
        elif tradingAction == TradingActionEnum.SELL:
            # Check if something can be selled
            sharesOfAppleInPortfolio = self.findSharesOfCompany(companyName, portfolio.shares)
            if (sharesOfAppleInPortfolio is not None):
                # Sell everything
                sharesOfCompany = SharesOfCompany(companyName, sharesOfAppleInPortfolio.amount);
                resultTradingActionList.addTradingAction(TradingAction(tradingAction, sharesOfCompany))

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
