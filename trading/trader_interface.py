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
    GOOGLE = "GOOG"
    APPLE = "AAPL"


class SharesOfCompany:
    '''
    Represents number of owned shares of one type (company) 
    '''

    def __init__(self, companyName: str, amountOfShares: int):
        """ Constructor
    
        Args:
          companyName : name of company
          amountOfShares : amount of shares
        """
        self.companyName = companyName
        self.amountOfShares = amountOfShares


class TradingAction:
    '''
    Represents action to be taken on a portfolio of a client
    '''

    def __init__(self, actionEnum: TradingActionEnum, sharesOfCompany: SharesOfCompany):
        """ Constructor
    
        Args:
          actionEnum : see TradingActionEnum
          sharesOfCompany : see SharesOfCompany
        """
        self.actionEnum = actionEnum
        self.sharesOfCompany = sharesOfCompany


class Portfolio:
    '''
    Represents portfolio of a client
    '''

    def __init__(self, cash: float, sharesOfCompanyList: list):
        """ Constructor
    
        Args:
          cash : current cash level
          sharesOfCompanyList : list of SharesOfCompany, see SharesOfCompany
        """
        self.cash = cash
        self.shares = sharesOfCompanyList

    def total_value(self, date: str, prices: dict):
        values = [share.amountOfShares * [price[1] for price in prices[share.companyName] if date == price[0]][0] for
                  share in self.shares]
        return sum(values) + self.cash


class StockMarketData:
    '''
    Represents current and historical stick market data of all companies
    '''

    def __init__(self, companyName2DateValueArrayDict: dict):
        """ Constructor
    
        Args:
          companyName2DateValueArrayDict : Dictionary containing current and historical data for all companies in Stock Market. 
                                           Structure: key: company name as string, value: 2 column array: datetime.date, float
        """
        self.companyName2DateValueArrayDict = companyName2DateValueArrayDict


class ITrader(metaclass=abc.ABCMeta):
    '''
    Trader interface.  
    '''

    @abc.abstractmethod
    def doTrade(self, portfolio: Portfolio, stockMarketData: StockMarketData) -> TradingAction:
        """ Generate action to be taken on the "stock market"
    
        Args:
          portfolio : current Portfolio of this trader
          stockMarketData : StockMarketData for evaluation
        Returns:
          An TradingAction instance
        """
        pass
