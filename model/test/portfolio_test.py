from unittest import TestCase

from datetime import date

from model.CompanyEnum import CompanyEnum
from model.Portfolio import Portfolio
from model.SharesOfCompany import SharesOfCompany
from model.StockData import StockData
from model.StockMarketData import StockMarketData
from model.Order import OrderList


class TestPortfolio(TestCase):
    def test_portfolio_construction(self):
        portfolio = Portfolio(1000.0,
                              [SharesOfCompany(CompanyEnum.COMPANY_A, 10), SharesOfCompany(CompanyEnum.COMPANY_B, 50)])

        assert portfolio.cash == 1000.0
        assert len(portfolio.shares) == 2
        assert portfolio.shares[0].company_enum == CompanyEnum.COMPANY_A
        assert portfolio.shares[0].amount == 10

        assert portfolio.shares[1].company_enum == CompanyEnum.COMPANY_B
        assert portfolio.shares[1].amount == 50

        assert f"{portfolio.cash}" in f"{portfolio}"

    def test_update__no_sufficient_cash_reserve(self):
        """
        Tests: Portfolio#update

        Flavour: Not enough cash in the portfolio, so no trades should be applied

        Creates a portfolio, a stock market data object and a arbitrary `OrderList` and executes these orders on the
        portfolio. Checks if those are applied correctly
        """
        cash_reserve = 10000.0

        data = StockData([(date(2017, 1, 1), 150.0)])
        stock_market_data = StockMarketData({CompanyEnum.COMPANY_A: data})

        portfolio = Portfolio(cash_reserve, [SharesOfCompany(CompanyEnum.COMPANY_A, 200)])
        order_list = OrderList()
        order_list.buy(CompanyEnum.COMPANY_A, 100)

        updated_portfolio = portfolio.update(stock_market_data, order_list)

        # Trade volume is too high for current cash reserve. Nothing should happen
        assert updated_portfolio.cash == cash_reserve
        assert updated_portfolio.cash == portfolio.cash
        assert updated_portfolio.shares[0].company_enum == CompanyEnum.COMPANY_A
        assert updated_portfolio.shares[0].amount == 200

    def test_update__sufficient_cash_reserve(self):
        """
        Tests: Portfolio#update

        Flavour: Enough cash in the portfolio, so the trades should be applied

        Creates a portfolio, a stock market data object and a arbitrary `OrderList` and executes these orders on the
        portfolio. Checks if those are applied correctly
        """
        cash_reserve = 20000.0

        data = StockData([(date(2017, 1, 1), 150.0)])
        stock_market_data = StockMarketData({CompanyEnum.COMPANY_A: data})

        portfolio = Portfolio(cash_reserve, [SharesOfCompany(CompanyEnum.COMPANY_A, 200)])

        order_list = OrderList()
        order_list.buy(CompanyEnum.COMPANY_A, 100)

        updated_portfolio = portfolio.update(stock_market_data, order_list)

        # Current cash reserve is sufficient for trade volume. Trade should happen
        assert updated_portfolio.cash < cash_reserve
        assert updated_portfolio.cash < portfolio.cash
        assert updated_portfolio.shares[0].company_enum == CompanyEnum.COMPANY_A
        assert updated_portfolio.shares[0].amount == 300

    def test_update__action_order_does_not_matter(self):
        """
        Tests: Portfolio#update

        Flavour: It shouldn't matter which order the orders are in, the result should always look the same. In
         this case the portfolio's cash reserve is too low to execute a BUY action. However, it shouldn't matter if we
         execute a SELL action first, because the updated cash reserve after a SELL action shouldn't affect the
         available cash reserve for a subsequent BUY action

        Creates a portfolio, a stock market data object and a arbitrary `OrderList` and executes these orders on the
        portfolio. Checks if those are applied correctly
        """
        cash_reserve = 10.0

        data = StockData([(date(2017, 1, 1), 150.0)])
        stock_market_data = StockMarketData({CompanyEnum.COMPANY_A: data})

        # Create two equal designed portfolios
        portfolio1 = Portfolio(cash_reserve, [SharesOfCompany(CompanyEnum.COMPANY_A, 200)])
        portfolio2 = Portfolio(cash_reserve, [SharesOfCompany(CompanyEnum.COMPANY_A, 200)])

        assert portfolio1 == portfolio2

        # Create two order lists with the same entries, however in different order
        order_list_1 = OrderList()
        order_list_1.buy(CompanyEnum.COMPANY_A, 100)
        order_list_1.sell(CompanyEnum.COMPANY_A, 100)

        order_list_2 = OrderList()
        order_list_2.sell(CompanyEnum.COMPANY_A, 100)
        order_list_2.buy(CompanyEnum.COMPANY_A, 100)

        # Execute the trade action lists on the two portfolios
        updated_portfolio_order1 = portfolio1.update(stock_market_data, order_list_1)
        updated_portfolio_order2 = portfolio2.update(stock_market_data, order_list_2)

        # The portfolios should still be equal after applying the actions
        assert updated_portfolio_order1 == updated_portfolio_order2

    def test_update__do_not_drop_below_cash_0(self):
        """
        Tests: Portfolio#update

        Flavour: When receiving two BUY orders the `#update` method should regard the available cash and NEVER drop
         below 0

        Creates a portfolio, a stock market data object and a arbitrary `OrderList` and executes these orders on the
        portfolio. Checks if those are applied correctly
        """
        cash_reserve = 16000.0

        data = StockData([(date(2017, 1, 1), 150.0)])
        stock_market_data = StockMarketData({CompanyEnum.COMPANY_A: data})

        portfolio = Portfolio(cash_reserve, [])

        # Create a order list whose individual actions are within the limit but in sum are over the limit
        # Stock price: 150.0, quantity: 100 -> trade volume: 15000.0; cash: 16000.0
        order_list = OrderList()
        order_list.buy(CompanyEnum.COMPANY_A, 100)
        order_list.buy(CompanyEnum.COMPANY_A, 100)

        updated_portfolio = portfolio.update(stock_market_data, order_list)

        assert updated_portfolio.cash >= 0

    def test_eq__wrong_instance(self):
        portfolio = Portfolio(10.0, [SharesOfCompany(CompanyEnum.COMPANY_A, 200)])

        assert portfolio != "a string"

    def test_eq__different_cash_reserve(self):
        portfolio1 = Portfolio(10.0, [SharesOfCompany(CompanyEnum.COMPANY_A, 200)])
        portfolio2 = Portfolio(100.0, [SharesOfCompany(CompanyEnum.COMPANY_A, 200)])

        assert portfolio1 != portfolio2

    def test_eq__different_stock_count__empty(self):
        portfolio1 = Portfolio(10.0, [SharesOfCompany(CompanyEnum.COMPANY_A, 200)])
        portfolio2 = Portfolio(10.0, [])

        assert portfolio1 != portfolio2

    def test_eq__different_stock_count__not_empty(self):
        portfolio1 = Portfolio(10.0, [SharesOfCompany(CompanyEnum.COMPANY_A, 200)])
        portfolio2 = Portfolio(10.0, [SharesOfCompany(CompanyEnum.COMPANY_A, 200),
                                      SharesOfCompany(CompanyEnum.COMPANY_B, 200)])

        assert portfolio1 != portfolio2

    def test_eq__different_stock_names(self):
        portfolio1 = Portfolio(10.0, [SharesOfCompany(CompanyEnum.COMPANY_A, 200)])
        portfolio2 = Portfolio(10.0, [SharesOfCompany(CompanyEnum.COMPANY_B, 200)])

        assert portfolio1 != portfolio2

    def test_eq__different_stock_quantity(self):
        portfolio1 = Portfolio(10.0, [SharesOfCompany(CompanyEnum.COMPANY_A, 200)])
        portfolio2 = Portfolio(10.0, [SharesOfCompany(CompanyEnum.COMPANY_A, 300)])

        assert portfolio1 != portfolio2

    def test_eq__equal(self):
        portfolio1 = Portfolio(10.0, [SharesOfCompany(CompanyEnum.COMPANY_A, 200)])
        portfolio2 = Portfolio(10.0, [SharesOfCompany(CompanyEnum.COMPANY_A, 200)])

        assert portfolio1 == portfolio2
