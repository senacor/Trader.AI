import abc

from model import Portfolio, StockMarketData
from model.Order import OrderList


class ITrader(metaclass=abc.ABCMeta):
    """
    Trader interface.
    """

    @abc.abstractmethod
    def doTrade(self, portfolio: Portfolio, current_portfolio_value: float,
                stock_market_data: StockMarketData) -> OrderList:
        """
        Generate action to be taken on the "stock market"

        Args:
          portfolio: The current Portfolio of this trader
          current_portfolio_value: The current value of the given portfolios
          stock_market_data: The stock market data for evaluation

        Returns:
          A list of orders, may be empty but never `None`
        """
        pass
