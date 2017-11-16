import datetime as dt
import json
from typing import Dict

import numpy
import random
from matplotlib import pyplot as plt
import os

from model.Portfolio import Portfolio
from model.StockMarketData import StockMarketData
from model.SharesOfCompany import SharesOfCompany
from model.CompanyEnum import CompanyEnum

"""
This file comprises some helpful functions to work with `Portfolios` and `StockMarketData`
"""

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
    :param name: The filename to read
    :param path: The path from which to read. Default: "../json/"
    :return: The created `Portfolio` object
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
    :param name: The names of the files to read
    :param path: The path from which to read. Default: "../datasets/"
    :return: The created `StockMarketData` object
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


def draw(portfolio_over_time: Dict[str, Dict[dt.datetime.date, Portfolio]], prices: StockMarketData):
    """
    Draws all given `Portfolios` based on the given `prices`
    :param portfolio_over_time:
    :param prices:
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
    :param stock_market_data: The `market_data` to step through
    :param offset: The offset to apply
    :return: A copied `StockMarketData` object which only reaches to position `offset`
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
    :param market_data: The `market_data` to check
    :return: `True` if all value rows have the same length, `False` if not
    """
    return len(set([len(values) for values in market_data.market_data.values()])) == 1
