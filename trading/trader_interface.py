'''
Created on 07.11.2017

Module contains interfaces for trader implementations and model classes

@author: jtymoszuk
'''
import abc
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
        
    def addTradingAction(self, tradingAction:TradingAction):
        self.tradingActionList.append(tradingAction)
        
    def len(self) -> int:
        return len(self.tradingActionList)
    
    def get(self, index:int) -> TradingAction:
        return self.tradingActionList[index]


class Portfolio:
    '''
    Represents portfolio of a client
    '''

    def __init__(self, cash: float, shares: list):
        """ Constructor
    
        Args:
          cash : current cash level
          shares : list of SharesOfCompany, see SharesOfCompany
        """
        self.cash = cash
        self.shares = shares

    def total_value(self, date: str, prices: dict):
        values = [share.amount * [price[1] for price in prices[share.name] if date == price[0]][0] for
                  share in self.shares]
        return sum(values) + self.cash

    def has_stock(self, name: str):
        return len(self.shares) != 0 and len([share for share in self.shares if share.name == name]) != 0

    def get_or_insert(self, name: str):
        if not self.has_stock(name):
            share = SharesOfCompany(name, 0)
            self.shares.append(share)
            return share

        return next(share for share in self.shares if share.name == name)


class StockMarketData:
    '''
    Represents current and historical stick market data of all companies
    '''

    def __init__(self, market_data: dict):
        """ Constructor
    
        Args:
          market_data : Dictionary containing current and historical data for all companies in Stock Market. 
                                           Structure: key: company name as string, value: 2 column array: datetime.date, float
        """
        self.market_data = market_data

    def get_most_recent_trade_day(self, stock: str):
        return self.market_data.get(stock)[-1][0]

    def get_most_recent_price(self, stock: str):
        return self.market_data.get(stock)[-1][1]


class ITrader(metaclass=abc.ABCMeta):
    '''
    Trader interface.  
    '''

    @abc.abstractmethod
    def doTrade(self, portfolio: Portfolio, stockMarketData: StockMarketData) -> TradingActionList:
        """ Generate action to be taken on the "stock market"
    
        Args:
          portfolio : current Portfolio of this trader
          stockMarketData : StockMarketData for evaluation
        Returns:
          An TradingAction instance
        """
        pass
