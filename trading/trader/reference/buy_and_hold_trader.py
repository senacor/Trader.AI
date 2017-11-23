"""
Created on 15.11.2017

@author: rmueller
"""
from model.ITrader import ITrader, OrderList, Portfolio
from model.StockMarketData import StockMarketData
from model.Order import CompanyEnum


class BuyAndHoldTrader(ITrader):
    """
    BuyAndHoldTrader buys 50% stock A and 50% stock B and holds them over time
    """

    def __init__(self):
        """
        Constructor
        """
        self.bought_stocks = False

    def doTrade(self, portfolio: Portfolio, current_portfolio_value: float,
                stock_market_data: StockMarketData) -> OrderList:
        """
        Generate action to be taken on the "stock market"
    
        Args:
          portfolio : current Portfolio of this trader
          current_portfolio_value : value of Portfolio at given Momemnt
          stock_market_data : StockMarketData for evaluation

        Returns:
          A OrderList instance, may be empty never None
        """
        if self.bought_stocks:
            return OrderList()
        else:
            self.bought_stocks = True
            order_list = OrderList()

            # Calculate how many cash to spend per company
            available_cash_per_stock = portfolio.cash / stock_market_data.get_number_of_companies()

            # Invest (100 // `len(companies)`)% of cash into each stock
            for company in list(CompanyEnum):
                most_recent_price = stock_market_data.get_most_recent_price(company)
                if most_recent_price is not None:
                    amount_to_buy = available_cash_per_stock // most_recent_price
                    order_list.buy(company, amount_to_buy)

        return order_list
