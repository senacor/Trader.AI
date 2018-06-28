"""
Created on 07.11.2017

This module contains everything related to orders

@author: jtymoszuk
"""
from enum import Enum

from model.CompanyEnum import CompanyEnum
from model.SharesOfCompany import SharesOfCompany


class OrderType(Enum):
    """
    Represents possible stock market order types
    """
    BUY = 1
    SELL = 2


class Order:
    """
    Represents an action to be taken on a portfolio
    """

    def __init__(self, action: OrderType, shares: SharesOfCompany):
        """
        Constructor
    
        Args:
          action: The order type
          shares: The stocks (name and quantity) to buy or sell
        """
        self.action = action
        self.shares = shares

    def __repr__(self) -> str:
        return f"<Order action=\"{self.action}\" shares=\"{self.shares}\">"


class OrderList:
    """
    Represents a type-safe container to hold a list of Orders
    """

    def __init__(self):
        """ 
        Constructor
        """
        self.__order_list = list()

    def __len__(self) -> int:
        """
        Returns the length of the underlying order list

        Returns:
            The underlying order list's length
        """
        return len(self.__order_list)

    def __getitem__(self, index: int) -> Order:
        """
        Returns the `index`nth element of the underlying order list

        Args:
            index: The item's index

        Returns:
            The underlying order list's `index`nth element
        """
        return self.__order_list[index]

    def __iter__(self):
        """
        Returns an iterator of the underlying order list

        Returns:
            The iterator
        """
        return iter(self.__order_list)

    def get_by_company_enum(self, company_enum: CompanyEnum) -> Order:
        """
        Returns an order for a given company, or `None` if nothing found

        Args:
            company_enum: The company to look up orders for

        Returns:
            The company's order or 'None' if nothing found
        """
        return next(
            (order for order in self.__order_list if
             order.shares.company_enum == company_enum),
            None)

    def is_empty(self):
        """
        Checks whether the underlying order list is empty

        Returns:
            `True` if the underlying order list is empty, `False` if not
        """
        return len(self) == 0

    def buy(self, company: CompanyEnum, amount: int):
        """
        Adds a order of type BUY to the list

        Args:
            company: The company to buy stocks of
            amount: The amount of stocks to buy
        """
        self.__add_order(OrderType.BUY, SharesOfCompany(company, amount))

    def sell(self, company: CompanyEnum, amount: int):
        """
        Adds a order of type SELL to the list

        Args:
            company: The company to sell stocks of
            amount: The amount of stocks to sell
        """
        self.__add_order(OrderType.SELL, SharesOfCompany(company, amount))

    def __add_order(self, order_type: OrderType, shares: SharesOfCompany):
        """
        Adds the given order to the list

        Args:
            order_type: The type of order to add
            shares: The stocks (name and quantity) to buy or sell
        """
        self.__order_list.append(Order(order_type, shares))

    def __repr__(self) -> str:
        return f"<OrderList orders=\"{self.__order_list}\">"
