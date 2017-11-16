'''
Created on 07.11.2017

Module contains interfaces for trader implementations and model classes

@author: jtymoszuk
'''
from enum import Enum

from model.CompanyEnum import CompanyEnum
from model.SharesOfCompany import SharesOfCompany


class TradingActionEnum(Enum):
    '''
    Represents possible actions on stock market
    '''
    BUY = 1
    SELL = 2


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
            (trading_action for trading_action in self.trading_action_list if
             trading_action.shares.company_enum == company_enum),
            None)

    def isEmpty(self):
        return len(self.trading_action_list) == 0
