import datetime as dt
from typing import Dict, List, Tuple

from matplotlib import pyplot as plt

from model.ITrader import ITrader
from model.Portfolio import Portfolio
from model.StockMarketData import StockMarketData

PortfoliosOverTime = Dict[str, Dict[dt.datetime.date, Portfolio]]
PortfolioNameTraderMappingList = List[Tuple[str, ITrader]]

"""
This file comprises some helpful functions to work with `Portfolios` and `StockMarketData`
"""


def draw(portfolio_over_time: PortfoliosOverTime, prices: StockMarketData):
    """
    Draws all given portfolios based on the given `prices`

    Args:
        portfolio_over_time: The portfolios to draw. Structure: `Dict[str, Dict[dt.datetime.date, Portfolio]]`
        prices: The prices on which the portfolios' performances should be calculated
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
        A copied `StockMarketData` object which only reaches from start to `offset`
    """
    if offset == 0:
        return stock_market_data

    offset_data = {}
    for company in stock_market_data.get_companies():
        offset_data[company] = stock_market_data[company].copy_to_offset(offset)

    return StockMarketData(offset_data)


def initialize_portfolios(cash: float, portfolio_trader_mappings: PortfolioNameTraderMappingList):
    """
    Creates a list of portfolios/trader tuples conveniently. Returns as many portfolios as `portfolio_trader_mappings`
    are given. Each portfolio is initialized with `cash` initial cash and an empty list of stocks

    Args:
        cash: The initial cash amount for *each* portfolio
        portfolio_trader_mappings: The portfolio name/trader mappings

    Returns:
        A list of tuples of portfolios and traders, one for/with each `portfolio_trader_mapping`
    """
    portfolios = list()

    for name, trader in portfolio_trader_mappings:
        portfolios.append((Portfolio(cash, [], name), trader))

    return portfolios
