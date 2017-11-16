import datetime as dt
import json
from typing import Dict, List

import numpy
import random
from matplotlib import pyplot as plt
import os

from definitions import DATASETS_DIR
from model.Portfolio import Portfolio
from model.StockMarketData import StockMarketData
from model.SharesOfCompany import SharesOfCompany
from model.CompanyEnum import CompanyEnum

"""
This file comprises some helpful functions to work with `Portfolios` and `StockMarketData`
"""

StockList = List[CompanyEnum]
PeriodList = List[str]

"""
Some JSON keys
"""
JSON_KEY_SHARES = 'shares'
JSON_KEY_COMPANY_ENUM = 'company_enum'
JSON_KEY_AMOUNT = 'amount'
JSON_KEY_CASH = 'cash'

"""
The csv's column keys
"""
DATE, OPEN, HIGH, LOW, CLOSE, ADJ_CLOSE, VOLUME = range(7)

"""
Colors `matplotlib` chooses randomly from to create graphs
"""
COLORS = ["red", "green", "blue", "orange", "purple", "pink", "yellow"]


def read_portfolio(name: str = 'portfolio', path="../json/") -> Portfolio:
    """
    Reads the JSON file from "../json/`name`.json" and creates a `Portfolio` object from this

    Args:
        name: The filename to read
        path: The path from which to read. Default: "../json/"

    Returns:
        The created `Portfolio` object
    """
    file = open(os.path.join(path, name + ".json"))
    data = json.loads(file.read())
    file.close()

    shares_list = list()
    for share in data[JSON_KEY_SHARES]:
        shares_list.append(SharesOfCompany(CompanyEnum[share[JSON_KEY_COMPANY_ENUM]], share[JSON_KEY_AMOUNT]))

    return Portfolio(data[JSON_KEY_CASH], shares_list)


def read_stock_market_data(company_enums_and_filenames_tuples: list, path: str = '../datasets/') -> StockMarketData:
    """
    Reads CSV files from "../`path`/`name`.csv" and creates a `StockMarketData` object from this

    Args:
        company_enums_and_filenames_tuples: Tuples of filenames and logical names used as dict keys
        path: The path from which to read. Default: "../datasets/"

    Returns:
        The created `StockMarketData` object
    """
    data = {}
    for company_enum, filename in company_enums_and_filenames_tuples:

        filepath = os.path.join(path, filename + '.csv')
        na_portfolio = numpy.loadtxt(filepath, dtype='|S15,f8,f8,f8,f8,f8,i8',
                                     delimiter=',', comments="#", skiprows=1)
        dates = list()
        for day in na_portfolio:
            date = dt.datetime.strptime(day[DATE].decode('UTF-8'), '%Y-%m-%d').date()
            dates.append((date, day[ADJ_CLOSE]))

        data[company_enum] = dates

    return StockMarketData(data)


def read_stock_market_data_conveniently(stocks: StockList, periods: PeriodList):
    """
    Reads the "cross product" from `stocks` and `periods` from CSV files and creates a `StockMarketData` object from
    this. For each defined stock in `stocks` the next available value from `CompanyEnum` is used as logical name. If
    there are `periods` provided those are each read.

    Args:
        stocks: The company names for which to read the stock data. *Important:* These values need to be stated in `CompanyEnum`
        periods: The periods to read. If not empty each period is appended to the filename like this: `[stock_name]_[period].csv`

    Returns:
        The created `StockMarketData` object

    Examples:
        * Preface: Provided stock names are supposed to be part to `CompanyEnum`. They are stated plaintext-ish here to show the point:
        * `(['stock_a', 'stock_b'], ['1962-2011', '2012-2017'])` reads:
            * 'stock_a_1962-2011.csv'
            * 'stock_a_2012-2017.csv'
            * 'stock_b_1962-2011.csv'
            * 'stock_b_2012-2017.csv'
          into a dict with keys `CompanyEnum.COMPANY_A` and `CompanyEnum.COMPANY_B` respectively
        * `(['stock_a'], ['1962-2011', '2012-2017'])` reads:
            * 'stock_a_1962-2011.csv'
            * 'stock_a_2012-2017.csv'
          into a dict with a key `CompanyEnum.COMPANY_A`
        * `(['stock_a', 'stock_b'], ['1962-2011'])` reads:
            * 'stock_a_1962-2011.csv'
            * 'stock_b_1962-2011.csv'
          into a dict with keys `CompanyEnum.COMPANY_A` and `CompanyEnum.COMPANY_B` respectively
        * `(['stock_a', 'stock_b'], [])` reads:
            * 'stock_a.csv'
            * 'stock_b.csv'
          into a dict with keys `CompanyEnum.COMPANY_A` and `CompanyEnum.COMPANY_B` respectively

    """
    data = dict()

    # Read *all* available data
    for stock in stocks:
        filename = stock.value
        if len(periods) is 0:
            data[stock] = read_stock_market_data([[stock, filename]], DATASETS_DIR)
        else:
            period_data = list()
            for period in periods:
                period_data.append(read_stock_market_data([[stock, ('%s_%s' % (filename, period))]], DATASETS_DIR))
            data[stock] = [item for sublist in period_data for item in sublist.market_data[stock]]

    return StockMarketData(data)


def draw(portfolio_over_time: Dict[str, Dict[dt.datetime.date, Portfolio]], prices: StockMarketData):
    """
    Draws all given `Portfolios` based on the given `prices`

    Args:
        portfolio_over_time:
        prices:
    """
    plt.figure()

    for name, portfolio in portfolio_over_time.items():
        values = [pf.total_value(date, prices.market_data) for date, pf in portfolio.items()]

        plt.plot(portfolio.keys(), values, label=name, color=random.choice(COLORS))

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
        offset_data[key] = value.copy()[:offset]

    return StockMarketData(offset_data)


def check_data_length(market_data):
    """
    Checks if the value rows of all keys inside `market_data` have the same count. Does this by extracting every
    row count, inserting those numbers into a set and checking if this set has the length of 1

    Args:
        market_data: The `market_data` to check

    Returns:
        `True` if all value rows have the same length, `False` if not
    """
    return len(set([len(values) for values in market_data.market_data.values()])) == 1
