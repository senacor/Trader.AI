import unittest
from unittest import TestCase

from datetime import date
import numpy as np

from model.CompanyEnum import CompanyEnum
from model.Portfolio import Portfolio
from model.SharesOfCompany import SharesOfCompany
from model.StockMarketData import StockMarketData
from utils import read_stock_market_data


def get_stock_market_data():
    return read_stock_market_data([CompanyEnum.COMPANY_A, CompanyEnum.COMPANY_B], ['1962-2011', '2012-2017'])


class TestStockMarketData(TestCase):
    def test_get_most_recent_trade_day(self):
        """
        Tests: StockMarketData#get_most_recent_trade_day

        Read the stock market data and check if the last available date is determined correctly
        """

        stock_market_data = get_stock_market_data()

        self.assertEqual(stock_market_data.get_most_recent_trade_day(),
                         stock_market_data.market_data[CompanyEnum.COMPANY_A].get_last()[0])

    def test_get_most_recent_price(self):
        """
        Tests: StockMarketData#get_most_recent_price

        Read the stock market data and check if the last available stock price is determined correctly
        """

        stock_market_data = get_stock_market_data()

        self.assertEqual(stock_market_data.get_most_recent_price(CompanyEnum.COMPANY_A),
                         stock_market_data.market_data[CompanyEnum.COMPANY_A].get_last()[1])

    def test_get_row_count(self):
        stock_market_data = get_stock_market_data()

        self.assertEqual(stock_market_data.get_row_count(),
                         stock_market_data.market_data[CompanyEnum.COMPANY_A].get_row_count())

    # TODO is that a good place for this test?
    def testStockMarketDataConstruction(self):
        companyName2DateValueArrayDict = dict()

        today = date(2017, 11, 8)
        yesterday = date(2017, 11, 8)
        date_value_array_1 = np.array([[today, yesterday], [10.0, 20.0]])
        companyName2DateValueArrayDict[CompanyEnum.COMPANY_A] = date_value_array_1

        date_value_array_2 = np.array([[today, yesterday], [1.0, 2.0]])
        companyName2DateValueArrayDict[CompanyEnum.COMPANY_B] = date_value_array_2

        stock_market_data = StockMarketData(companyName2DateValueArrayDict)
        stock_market_data.market_data.items()

    # TODO is that a good place for this test?
    def testPortfolioConstruction(self):
        shares_of_company_list = list()
        shares_of_company_a = SharesOfCompany(CompanyEnum.COMPANY_A, 10)
        shares_of_company_b = SharesOfCompany(CompanyEnum.COMPANY_B, 50)
        shares_of_company_list.append(shares_of_company_a)
        shares_of_company_list.append(shares_of_company_b)

        portfolio = Portfolio(1000.0, shares_of_company_list)

        self.assertEqual(portfolio.cash, 1000.0)
        self.assertEqual(len(portfolio.shares), 2)
        self.assertEqual(portfolio.shares[0].company_enum, CompanyEnum.COMPANY_A)
        self.assertEqual(portfolio.shares[0].amount, 10)

        self.assertEqual(portfolio.shares[1].company_enum, CompanyEnum.COMPANY_B)
        self.assertEqual(portfolio.shares[1].amount, 50)
