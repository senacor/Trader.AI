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
    COMPANY_A = "AAPL"
    COMPANY_B = "GOOG"


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
        self.tradingActionList = list()

    def addTradingAction(self, tradingAction: TradingAction):
        self.tradingActionList.append(tradingAction)

    def len(self) -> int:
        return len(self.tradingActionList)

    def get(self, index: int) -> TradingAction:
        return self.tradingActionList[index]

    def isEmpty(self):
        return len(self.tradingActionList) == 0


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
        self.name = name
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

        for trade_action in trade_action_list.tradingActionList:
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


class ITrader(metaclass=abc.ABCMeta):
    """
    Trader interface.
    """

    @abc.abstractmethod
    def doTrade(self, portfolio: Portfolio, currentPortfolioValue: float, stockMarketData: StockMarketData,
                company_a_name=CompanyEnum.COMPANY_A.value,
                company_b_name=CompanyEnum.COMPANY_B.value) -> TradingActionList:
        """ Generate action to be taken on the "stock market"
    
        Args:
          portfolio : current Portfolio of this trader
          currentPortfolioValue : value of Portfolio at given Momemnt
          stockMarketData : StockMarketData for evaluation
          company_a_name : optional name of 1st company, or default
          company_b_name : optional name of 2nd company, or default
        Returns:
          A TradingActionList instance, may be empty never None
        """
        pass
