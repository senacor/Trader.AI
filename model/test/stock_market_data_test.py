import unittest
from unittest import TestCase

from datetime import date
import numpy as np

from definitions import PERIOD_1, PERIOD_2
from model.CompanyEnum import CompanyEnum
from model.Portfolio import Portfolio
from model.SharesOfCompany import SharesOfCompany
from model.StockMarketData import StockMarketData
from utils import read_stock_market_data


def get_stock_market_data():
    return read_stock_market_data([CompanyEnum.COMPANY_A, CompanyEnum.COMPANY_B], [PERIOD_1, PERIOD_2])


class TestStockMarketData(TestCase):
    def test_get_most_recent_trade_day(self):
        """
        Tests: StockMarketData#get_most_recent_trade_day

        Read the stock market data and check if the last available date is determined correctly
        """

        stock_market_data = get_stock_market_data()

        assert stock_market_data.get_most_recent_trade_day() == stock_market_data[CompanyEnum.COMPANY_A].get_last()[0]

    def test_get_most_recent_price(self):
        """
        Tests: StockMarketData#get_most_recent_price

        Read the stock market data and check if the last available stock price is determined correctly
        """

        stock_market_data = get_stock_market_data()

        assert stock_market_data.get_most_recent_price(CompanyEnum.COMPANY_A) == \
               stock_market_data[CompanyEnum.COMPANY_A].get_last()[1]

    def test_get_row_count(self):
        stock_market_data = get_stock_market_data()

        assert stock_market_data.get_row_count() == stock_market_data[CompanyEnum.COMPANY_A].get_row_count()
