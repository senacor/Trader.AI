import abc

from model import Portfolio, StockMarketData
from trading.trader_interface import TradingActionList


class ITrader(metaclass=abc.ABCMeta):
    """
    Trader interface.
    """

    @abc.abstractmethod
    def doTrade(self, portfolio: Portfolio, current_portfolio_value: float,
                stock_market_data: StockMarketData) -> TradingActionList:
        """ Generate action to be taken on the "stock market"

        Args:
          portfolio : current Portfolio of this trader
          current_portfolio_value : value of Portfolio at given Momemnt
          stock_market_data : StockMarketData for evaluation
        Returns:
          A TradingActionList instance, may be empty never None
        """
        pass
