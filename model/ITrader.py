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
        """ Generate action to be taken on the "stock market"

        Args:
          portfolio : current Portfolio of this trader
          current_portfolio_value : value of Portfolio at given Momemnt
          stock_market_data : StockMarketData for evaluation
        Returns:
          A OrderList instance, may be empty never None
        """
        pass
