'''
Created on 07.11.2017

Module contains interfaces for trader implementations and model classes

@author: jtymoszuk
'''
import copy

import abc
import datetime
from enum import Enum


class TradingActionEnum(Enum):
    '''
    Represents possible actions on stock market
    '''
    BUY = 1
    SELL = 2


class CompanyEnum(Enum):
    '''
    Represents companies on stock market
    '''
    COMPANY_A = "stock_a"
    COMPANY_B = "stock_b"


class SharesOfCompany:
    '''
    Represents number of owned shares of one type (company) 
    '''

    def __init__(self, name: str, amount: int):
        """ Constructor
    
        Args:
          name : name of company
          amount : amount of shares
        """
        self.name = name
        self.amount = amount


class TradingAction:
    '''
    Represents action to be taken on a portfolio of a client
    '''

    def __init__(self, action: TradingActionEnum, shares: SharesOfCompany):
        """ Constructor
    
        Args:
          action : see TradingActionEnum
          shares : see SharesOfCompany
        """
        self.action = action
        self.shares = shares


class TradingActionList:
    '''
    Represents typesafe container to hold a list of TradingAction's
    '''

    def __init__(self):
        """ 
        Constructor
        """
        self.trading_action_list = list()

    def addTradingAction(self, trading_action: TradingAction):
        self.trading_action_list.append(trading_action)

    def len(self) -> int:
        return len(self.trading_action_list)

    def get(self, index: int) -> TradingAction:
        return self.trading_action_list[index]

    def get_by_CompanyEnum(self, company_enum: CompanyEnum) -> TradingAction:
        """
        Returns TradingAction for given CompanyEnum, or None if nothing found
        """
        return next(
            (trading_action for trading_action in self.trading_action_list if trading_action.shares.name == company_enum.value),
            None)

    def isEmpty(self):
        return len(self.trading_action_list) == 0


class StockMarketData:
    """
    Represents current and historical stick market data of all companies
    """

    def __init__(self, market_data: dict):
        """
        Constructor
        :param market_data: Dictionary containing current and historical data for all companies in Stock Market.
        Structure: key: company name as string, value: 2 column array: datetime.date, float
        """
        self.market_data = market_data

    def get_most_recent_trade_day(self):
        return next(iter(self.market_data.values()))[-1][0]

    def get_most_recent_price(self, stock: str):
        return self.market_data.get(stock)[-1][1]

    def get_row_count(self):
        return len(next(iter(self.market_data.values())))

    def get_stock_data_for_company(self, company_enum: CompanyEnum):
        """
        Delivers data for given CompanyEnum, or None if nothing found
        """
        return self.market_data.get(company_enum.value)


class Portfolio:
    """
    Represents portfolio of a client
    """

    def __init__(self, cash: float, shares: list, name: str = 'nameless'):
        """ Constructor

        Args:
          cash : current cash level
          shares : list of SharesOfCompany, see SharesOfCompany
        """
        self.name = name  # TODO wo brauchen wir name?
        self.cash = cash
        self.shares = shares

    def total_value(self, date: datetime.date, prices: dict):
        values = [share.amount *
                  [price[1] for price in prices[share.name] if date == price[0]][0]
                  for share in self.shares]

        return sum(values) + self.cash

    def has_stock(self, name: str):
        return len(self.shares) != 0 and len([share for share in self.shares if share.name == name]) != 0

    def get_or_insert(self, name: str):
        if not self.has_stock(name):
            share = SharesOfCompany(name, 0)
            self.shares.append(share)
            return share

        return next(share for share in self.shares if share.name == name)

    # TODO comment
    # TODO refactor: get rid of SharesOfCompany? do we really use that object somewhere?
    def get_by_name(self, name: str) -> SharesOfCompany:
        """
            Returns SharesOfCompany for company name, or None if nothing found
        """
        return next((share for share in self.shares if share.name == name), None)

    # Return the amount of shares we hold from the given company.
    # If we don't hold any shares of this company, we return 0.
    def get_amount(self, company_name: str) -> int:
        share = self.get_by_name(company_name)
        if share is not None:
            return share.amount
        else:
            return 0

    def update(self, stock_market_data: StockMarketData, trade_action_list: TradingActionList):
        """
        Iterates through the list of trading actions (`trade_action_list`), applies those actions and returns an updated
        `Portfolio` object based on the given `StockMarketData`. If `trade_action_list` is empty nothing will be changed
        :param stock_market_data: The market data based on which the actions are applied
        :param trade_action_list: The list of trading action to apply
        :return: An updated portfolio. This is a deep copy of the given `portfolio` (see `copy.deepcopy`)
        """
        updated_portfolio = copy.deepcopy(self)

        print(f"\nUpdate portfolio {self.name}")

        if trade_action_list.isEmpty():
            print("No action this time")
            return updated_portfolio

        for trade_action in trade_action_list.trading_action_list:
            shares_name = trade_action.shares.name

            current_date = stock_market_data.get_most_recent_trade_day()
            current_price = stock_market_data.get_most_recent_price(shares_name)

            print(f"Available cash on {current_date}: {updated_portfolio.cash}")
            # for share in update.shares:
            share = updated_portfolio.get_or_insert(shares_name)
            # if share.name is update.shares.name:
            amount = trade_action.shares.amount
            trade_volume = amount * current_price

            if trade_action.action is TradingActionEnum.BUY:
                print(f"  Buying {amount} shares of '{share.name}' with an individual value of {current_price}")
                print(f"  Volume of this trade: {trade_volume}")

                if trade_volume <= updated_portfolio.cash:
                    share.amount += amount
                    updated_portfolio.cash -= trade_volume
                else:
                    print(f"  No sufficient cash reserve ({updated_portfolio.cash}) for planned transaction with "
                          f"volume of {trade_volume}")
            elif trade_action.action is TradingActionEnum.SELL:
                print(f"  Selling {amount} shares of {share.name} with individual value of {current_price}")
                print(f"  Volume of this trade: {trade_volume}")

                if share.amount > amount:
                    share.amount -= amount
                    updated_portfolio.cash += trade_volume
                else:
                    print(f"  Not sufficient shares in portfolio ({amount}) for planned sale of {share.amount} shares")

            print(f"Resulting available cash after trade: {updated_portfolio.cash}")

            total_portfolio_value = updated_portfolio.total_value(current_date, stock_market_data.market_data)
            print(f"Total portfolio value after trade: {total_portfolio_value}")

        return updated_portfolio
    
    def isTradingActionListValid(self, tradingActionList : TradingActionList, stockMarketData: StockMarketData) -> bool:
        """
        Validates if generated TradingActionList is valid in comparison to current Portfolio
        Args:
          trading_action_list : TradingActionList containing generated TradingAction's to be sent into Evaluation (Stock Market)
          stockMarketData: StockMarketData containing date for all companies 
        Returns:
          A True if given TradingActionList is valid in comparison to current Portfolio, False otherwise, never None
        """
        
        current_cash = self.cash

        most_recent_price_company_a = stockMarketData.get_most_recent_price(CompanyEnum.COMPANY_A.value)
        trading_action_for_company_a = tradingActionList.get_by_CompanyEnum(CompanyEnum.COMPANY_A)
        
        is_valid, current_cash = self.__isTradingActionValid(current_cash, CompanyEnum.COMPANY_A.value, trading_action_for_company_a, most_recent_price_company_a)
        if(is_valid is False):
            return False
        
        most_recent_price_company_b = stockMarketData.get_most_recent_price(CompanyEnum.COMPANY_B.value)
        trading_action_for_company_b = tradingActionList.get_by_CompanyEnum(CompanyEnum.COMPANY_B)
        
        is_valid, current_cash = self.__isTradingActionValid(current_cash, CompanyEnum.COMPANY_B.value, trading_action_for_company_b, most_recent_price_company_b)
        if(is_valid is False):
            return False
        
        return True

    def __isTradingActionValid(self, current_cash: float, company_name: str, trading_action_for_company: TradingAction, most_recent_price_company: float):
        """
        Validates if given TradingAction is valid
        Args:
          current_cash : TradingActionList containing generated TradingAction's to be sent into Evaluation (Stock Market)
          company_name : Company name as String
          trading_action_for_company: TradingAction
          most_recent_price_company: most recent price of company as float 
        Returns:
          A True if given TradingAction is valid in comparison to current Portfolio and Cash, False otherwise, never None
        """
        if(trading_action_for_company is not None):
            if(trading_action_for_company.action == TradingActionEnum.BUY):
                price_to_pay = most_recent_price_company * trading_action_for_company.shares
                
                current_cash = current_cash - price_to_pay
                if(current_cash < 0):
                    # TODO: use Logging!!!
                    print(f"!!!! RnnTrader - WARNING: Not enough money to pay! tradingActionForCompany: {trading_action_for_company}, Portfolio: {self}")
                    return False, current_cash
                
            elif (trading_action_for_company.action == TradingActionEnum.SELL):
                if (trading_action_for_company.shares > self.get_amount(company_name)):
                    return False
            else:
                raise ValueError(f'Action for tradingActionForCompanyB is not valid: {trading_action_for_company}') 
            
        return True, current_cash




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
