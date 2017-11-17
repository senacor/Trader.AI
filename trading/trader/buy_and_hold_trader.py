'''
Created on 15.11.2017

@author: rmueller
'''
from model.ITrader import ITrader, TradingActionList, Portfolio
from model.StockMarketData import StockMarketData
from model.trader_actions import CompanyEnum


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

            companies = list(CompanyEnum)

            available_cash_per_stock = portfolio.cash / len(companies)

            # Invest (100 // `len(companies)`)% of cash into each stock
            for company in companies:
                amount_to_buy = available_cash_per_stock // stockMarketData.get_most_recent_price(company)
                trading_actions.buy(company, amount_to_buy)

        return trading_actions
