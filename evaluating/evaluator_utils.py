import datetime as dt
import json
from typing import Dict

from matplotlib import pyplot as plt
import os

from model.Portfolio import Portfolio
from model.StockMarketData import StockMarketData
from model.SharesOfCompany import SharesOfCompany
from model.CompanyEnum import CompanyEnum

"""
This file comprises some helpful functions to work with `Portfolios` and `StockMarketData`
"""

def draw(portfolio_over_time: Dict[str, Dict[dt.datetime.date, Portfolio]], prices: StockMarketData):
    """
    Draws all given `Portfolios` based on the given `prices`

    Args:
        portfolio_over_time:
        prices:
    """
    plt.figure()

    for name, portfolio in portfolio_over_time.items():
        values = [pf.total_value(date, prices) for date, pf in portfolio.items()]
        plt.plot(portfolio.keys(), values, label=name)

    plt.legend(portfolio_over_time.keys())
    plt.show()


def get_data_up_to_offset(stock_market_data: StockMarketData, offset: int):
    """
    Removes all data items *behind* the given `offset` - this emulates going through history in a list of
    date->price items

    Args:
        stock_market_data: The `market_data` to step through
        offset: The offset to apply

    Returns:
        A copied `StockMarketData` object which only reaches to position `offset`
    """
    if offset == 0:
        return stock_market_data

    offset_data = {}
    for key, value in stock_market_data.market_data.items():
        offset_data[key] = value.copy_to_offset(offset)

    return StockMarketData(offset_data)
