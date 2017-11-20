from unittest import TestCase

from datetime import date

from model.CompanyEnum import CompanyEnum
from model.Portfolio import Portfolio
from model.SharesOfCompany import SharesOfCompany
from model.StockData import StockData
from model.StockMarketData import StockMarketData
from model.trader_actions import TradingActionList


class TestPortfolio(TestCase):
    def testPortfolioConstruction(self):
        portfolio = Portfolio(1000.0,
                              [SharesOfCompany(CompanyEnum.COMPANY_A, 10), SharesOfCompany(CompanyEnum.COMPANY_B, 50)])

        self.assertEqual(portfolio.cash, 1000.0)
        self.assertEqual(len(portfolio.shares), 2)
        self.assertEqual(portfolio.shares[0].company_enum, CompanyEnum.COMPANY_A)
        self.assertEqual(portfolio.shares[0].amount, 10)

        self.assertEqual(portfolio.shares[1].company_enum, CompanyEnum.COMPANY_B)
        self.assertEqual(portfolio.shares[1].amount, 50)

    def testUpdatePortfolio_noSufficientCashReserve(self):
        """
        Tests: Portfolio#update

        Flavour: Not enough cash in the portfolio, so no trades should be applied

        Creates a portfolio, a stock market data object and a arbitrary `TradingActionList` and executes this trading
        actions on the portfolio. Checks if those are applied correctly
        """
        cash_reserve = 10000.0

        data = StockData([(date(2017, 1, 1), 150.0)])
        stock_market_data = StockMarketData({CompanyEnum.COMPANY_A: data})

        portfolio = Portfolio(cash_reserve, [SharesOfCompany(CompanyEnum.COMPANY_A, 200)])
        trading_action_list = TradingActionList()
        trading_action_list.buy(CompanyEnum.COMPANY_A, 100)

        updated_portfolio = portfolio.update(stock_market_data, trading_action_list)

        # Trade volume is too high for current cash reserve. Nothing should happen
        self.assertEqual(updated_portfolio.cash, cash_reserve)
        self.assertEqual(updated_portfolio.cash, portfolio.cash)
        self.assertEqual(updated_portfolio.shares[0].company_enum, CompanyEnum.COMPANY_A)
        self.assertEqual(updated_portfolio.shares[0].amount, 200)

    def testUpdatePortfolio_sufficientCashReserve(self):
        """
        Tests: Portfolio#update

        Flavour: Enough cash in the portfolio, so the trades should be applied

        Creates a portfolio, a stock market data object and a arbitrary `TradingActionList` and executes this trading
        actions on the portfolio. Checks if those are applied correctly
        """
        cash_reserve = 20000.0

        data = StockData([(date(2017, 1, 1), 150.0)])
        stock_market_data = StockMarketData({CompanyEnum.COMPANY_A: data})

        portfolio = Portfolio(cash_reserve, [SharesOfCompany(CompanyEnum.COMPANY_A, 200)])

        trading_action_list = TradingActionList()
        trading_action_list.buy(CompanyEnum.COMPANY_A, 100)

        updated_portfolio = portfolio.update(stock_market_data, trading_action_list)

        # Current cash reserve is sufficient for trade volume. Trade should happen
        self.assertLess(updated_portfolio.cash, cash_reserve)
        self.assertLess(updated_portfolio.cash, portfolio.cash)
        self.assertEqual(updated_portfolio.shares[0].company_enum, CompanyEnum.COMPANY_A)
        self.assertEqual(updated_portfolio.shares[0].amount, 300)
