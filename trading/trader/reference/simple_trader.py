"""
Created on 08.11.2017

@author: jtymoszuk
"""
from model.Portfolio import Portfolio
from model.StockData import StockData
from model.StockMarketData import StockMarketData
from model.ITrader import ITrader
from model.Order import OrderList
from model.Order import OrderType
from model.Order import SharesOfCompany
from model.Order import CompanyEnum
from model.IPredictor import IPredictor
import copy
from logger import logger


class SimpleTrader(ITrader):
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
        local_portfolio = copy.deepcopy(portfolio)

        result = OrderList()

        company_a_data = stock_market_data[CompanyEnum.COMPANY_A]
        if self.stock_a_predictor is not None and company_a_data is not None:
            self.__trade_for_company(CompanyEnum.COMPANY_A, company_a_data, self.stock_a_predictor, local_portfolio,
                                     result)
        else:
            logger.warning(f" stock_a_predictor:  {self.stock_a_predictor} or company_a_data: {company_a_data} is None "
                           f"-> No prediction for Company A")

        company_b_data = stock_market_data[CompanyEnum.COMPANY_B]
        if self.stock_b_predictor is not None and company_b_data is not None:
            self.__trade_for_company(CompanyEnum.COMPANY_B, company_b_data, self.stock_b_predictor, local_portfolio,
                                     result)
        else:
            logger.warning("stock_b_predictor or company_b_data is None -> No prediction for Company B")

        return result

    def __trade_for_company(self, company_enum: CompanyEnum, company_data: StockData, predictor: IPredictor,
                            portfolio: Portfolio, result_order_list: OrderList):

        last_value = company_data.get_last()[-1]

        # This determines the trade action to apply
        order = self.__determine_action(company_data, predictor, last_value)

        if order == OrderType.BUY:
            if portfolio.cash > last_value:
                # We can buy something
                amount_of_units_to_buy = int(portfolio.cash // last_value)
                result_order_list.buy(company_enum, amount_of_units_to_buy)

                # Update Cash in portfolio
                portfolio.cash = portfolio.cash - (amount_of_units_to_buy * last_value)

        elif order == OrderType.SELL:
            # Check if something can be selled
            shares_in_portfolio = self.__find_shares_of_company(company_enum, portfolio.shares)
            if shares_in_portfolio is not None:
                # Sell everything
                result_order_list.sell(company_enum, shares_in_portfolio.amount)

    def __determine_action(self, company_data, predictor, last_value):
        predicted_next_value = predictor.doPredict(company_data)

        action = None
        if predicted_next_value > last_value:
            action = OrderType.BUY
        elif predicted_next_value < last_value:
            action = OrderType.SELL

        return action

    def __find_shares_of_company(self, company_enum: CompanyEnum, shares: list) -> SharesOfCompany:
        """
        Finds SharesOfCompany in list by company name
    
        Args:
          company_enum : company to find
          shares: list with SharesOfCompany

        Returns:
          SharesOfCompany for given company or None 
        """
        for shares_of_company in shares:
            if isinstance(shares_of_company, SharesOfCompany) and shares_of_company.company_enum == company_enum:
                return shares_of_company

        return None
