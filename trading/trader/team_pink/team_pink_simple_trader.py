"""
Created on 08.11.2017

@author: jtymoszuk
"""
from model.Portfolio import Portfolio
from model.StockMarketData import StockMarketData
from model.ITrader import ITrader
from model.Order import OrderList
from model.IPredictor import IPredictor


class TeamPinkSimpleTrader(ITrader):
    """
    Simple Trader generates Order based on simple logic, input data and prediction from NN-Engine
    """

    def __init__(self, stock_a_predictor: IPredictor, stock_b_predictor: IPredictor):
        """
        Constructor
        """
        self.stock_a_predictor = stock_a_predictor
        self.stock_b_predictor = stock_b_predictor

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

        result = OrderList()

        # TODO: implement trading logic

        return result
