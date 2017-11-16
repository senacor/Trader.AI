'''
Created on 08.11.2017

@author: jtymoszuk
'''
from model.Portfolio import Portfolio
from model.StockMarketData import StockMarketData
from trading.ITrader import ITrader
from trading.trader_interface import TradingActionList
from trading.trader_interface import TradingAction
from trading.trader_interface import TradingActionEnum
from trading.trader_interface import SharesOfCompany
from trading.trader_interface import CompanyEnum
from predicting.predictor_interface import IPredictor
import copy


class SimpleTrader(ITrader):
    '''
    Simple Trader generates TradingAction based on simple logic, input data and prediction from NN-Engine
    '''

    def __init__(self, stock_a_predictor: IPredictor, stock_b_predictor: IPredictor):
        '''
        Constructor
        '''
        self.stock_a_predictor = stock_a_predictor
        self.stock_b_predictor = stock_b_predictor

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

        local_portfolio = copy.deepcopy(portfolio)

        result = TradingActionList()

        company_a_data = stock_market_data.market_data.get(CompanyEnum.COMPANY_A.value)
        if (self.stock_a_predictor is not None and company_a_data is not None):
            self.__trade_for_company(CompanyEnum.COMPANY_A.value, company_a_data, self.stock_a_predictor, local_portfolio,
                                 result)
        else:
            # TODO: use Logging!!!
            print("!!!! SimpleTrader: stock_a_predictor or company_a_data is None -> No prediction for Company A")

        company_b_data = stock_market_data.market_data.get(CompanyEnum.COMPANY_B.value)
        if (self.stock_b_predictor is not None and company_b_data is not None):
            self.__trade_for_company(CompanyEnum.COMPANY_B.value, company_b_data, self.stock_b_predictor, local_portfolio,
                                 result)
        else:
            # TODO: use Logging!!!
            print("!!!! SimpleTrader: stock_b_predictor or company_b_data is None -> No prediction for Company B")

        return result

    def __trade_for_company(self, company_name: str, company_data: list, predictor: IPredictor, portfolio: Portfolio,
                        result_trading_action_list: TradingActionList):

        lastValue = company_data[-1][-1]

        # This determines the trade action to apply
        trading_action = self.__determine_action(company_data, predictor, lastValue)

        if trading_action == TradingActionEnum.BUY:
            if (portfolio.cash > lastValue):
                # We can buy something
                amount_of_units_to_buy = int(portfolio.cash // lastValue)
                shares_of_company = SharesOfCompany(company_name, amount_of_units_to_buy);
                result_trading_action_list.addTradingAction(TradingAction(trading_action, shares_of_company))

                # Update Cash in portfolio
                portfolio.cash = portfolio.cash - (amount_of_units_to_buy * lastValue)

        elif trading_action == TradingActionEnum.SELL:
            # Check if something can be selled
            shares_of_apple_in_portfolio = self.__find_shares_of_company(company_name, portfolio.shares)
            if (shares_of_apple_in_portfolio is not None):
                # Sell everything
                shares_of_company = SharesOfCompany(company_name, shares_of_apple_in_portfolio.amount);
                result_trading_action_list.addTradingAction(TradingAction(trading_action, shares_of_company))

    def __determine_action(self, company_data, predictor, last_value):
        predicted_next_apple_value = predictor.doPredict(company_data)

        action = None
        if predicted_next_apple_value > last_value:
            action = TradingActionEnum.BUY
        elif predicted_next_apple_value < last_value:
            action = TradingActionEnum.SELL

        return action

    def __find_shares_of_company(self, company_name: str, shares: list) -> SharesOfCompany:
        """ Finds SharesOfCompany in list by company name
    
        Args:
          company_name : company to find
          list : list with SharesOfCompany
        Returns:
          SharesOfCompany for given company or None 
        """
        for shares_of_company in shares:
            if (isinstance(shares_of_company, SharesOfCompany) and shares_of_company.name == company_name):
                return shares_of_company

        return None