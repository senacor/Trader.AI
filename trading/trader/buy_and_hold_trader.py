'''
Created on 15.11.2017

@author: rmueller
'''
from trading.model.ITrader import ITrader, TradingActionList, Portfolio
from trading.model.trader_interface import TradingAction
from model.StockMarketData import StockMarketData
from trading.model.trader_interface import TradingActionEnum
from trading.model.trader_interface import SharesOfCompany
from trading.model.trader_interface import CompanyEnum


class BuyAndHoldTrader(ITrader):
    '''
    BuyAndHoldTrader buys 50% stock A and 50% stock B and holds them over time
    '''
    def __init__(self):
        '''
        Constructor
        '''
        self.bought_stocks = False

    def doTrade(self, portfolio: Portfolio, currentPortfolioValue: float,
                stockMarketData: StockMarketData) -> TradingActionList:
        """ Generate action to be taken on the "stock market"
    
        Args:
          portfolio : current Portfolio of this trader
          currentPortfolioValue : value of Portfolio at given Momemnt
          stockMarketData : StockMarketData for evaluation
        Returns:
          A TradingActionList instance, may be empty never None
        """
        if self.bought_stocks:
            return TradingActionList()
        else:
            self.bought_stocks = True
            trading_actions = TradingActionList()
            available_cash_per_stock = portfolio.cash / 2 # TODO can we infer the 2 from CompanyEnum?

            # Invest 50% of cash into stock A
            # TODO @janusz
            # Das folgende Beispiel illustriert was ich meine mit "in zu vielen Objekte verpackt".
            # Eigentlich möchte ich nur sowas schreiben wie:
            #
            # trading_actions.buy(stock, amount)
            #
            # Stattdessen muss ich folgendes schreiben:
            amount_to_buy = available_cash_per_stock // stockMarketData.get_most_recent_price(CompanyEnum.COMPANY_A)
            amount_to_buy_wrapped_in_object = SharesOfCompany(CompanyEnum.COMPANY_A, amount_to_buy)
            amount_to_buy_wrapped_in_another_object = TradingAction(TradingActionEnum.BUY, amount_to_buy_wrapped_in_object)
            trading_actions.addTradingAction(amount_to_buy_wrapped_in_another_object)

            # Invest 50% of cash into stock B
            amount_to_buy = available_cash_per_stock // stockMarketData.get_most_recent_price(CompanyEnum.COMPANY_B)
            amount_to_buy_wrapped_in_object = SharesOfCompany(CompanyEnum.COMPANY_B, amount_to_buy)
            amount_to_buy_wrapped_in_another_object = TradingAction(TradingActionEnum.BUY, amount_to_buy_wrapped_in_object)
            trading_actions.addTradingAction(amount_to_buy_wrapped_in_another_object)
        return trading_actions