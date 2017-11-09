'''
Created on 08.11.2017

Module for testing of the evaluating component

@author: jholtkamp
'''
import unittest

from evaluating.evaluator import read_portfolio, read_stock_market_data, update_portfolio
from trading.simple_trader import SimpleTrader
from trading.trader_interface import CompanyEnum, TradingAction, TradingActionEnum, SharesOfCompany, Portfolio, \
    StockMarketData


class EvaluatorTest(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testReadPortfolio(self):
        portfolio = read_portfolio()

        self.assertEqual(len(portfolio.shares), 2)
        self.assertEqual(portfolio.cash, 10000.0)
        self.assertEqual(portfolio.shares[0].companyName, CompanyEnum.GOOGLE.value)

    def testReadStockMarketData(self):
        apple = CompanyEnum.APPLE.value
        google = CompanyEnum.GOOGLE.value

        stock_market_data = read_stock_market_data([apple, google])

        self.assertGreater(len(stock_market_data.companyName2DateValueArrayDict), 0)
        self.assertTrue(apple in stock_market_data.companyName2DateValueArrayDict)
        self.assertTrue(google in stock_market_data.companyName2DateValueArrayDict)

    def testDoTrade(self):
        apple = CompanyEnum.APPLE.value

        trading_action = SimpleTrader().doTrade(read_portfolio(), read_stock_market_data([apple]))

        if trading_action is not None:
            self.assertEqual(trading_action.sharesOfCompany.companyName, apple)

    def testUpdatePortfolio_noSufficientCashReserve(self):
        cash_reserve = 10000.0
        symbol = CompanyEnum.APPLE.value

        data = list()
        data.append(('2017-01-01', 150.0))
        stock_market_data = StockMarketData({symbol: data})

        portfolio = Portfolio(cash_reserve, [SharesOfCompany(symbol, 200)])
        update = TradingAction(TradingActionEnum.BUY, SharesOfCompany(symbol, 100))
        updated_portfolio = update_portfolio(stock_market_data, portfolio, update)

        # Trade volume is too high for current cash reserve. Nothing should happen
        self.assertEqual(updated_portfolio.cash, cash_reserve)
        self.assertEqual(updated_portfolio.cash, portfolio.cash)
        self.assertEqual(updated_portfolio.shares[0].companyName, symbol)
        self.assertEqual(updated_portfolio.shares[0].amountOfShares, 200)

    def testUpdatePortfolio_sufficientCashReserve(self):
        cash_reserve = 20000.0
        symbol = CompanyEnum.APPLE.value

        data = list()
        data.append(('2017-01-01', 150.0))
        stock_market_data = StockMarketData({symbol: data})

        portfolio = Portfolio(cash_reserve, [SharesOfCompany(symbol, 200)])
        update = TradingAction(TradingActionEnum.BUY, SharesOfCompany(symbol, 100))
        updated_portfolio = update_portfolio(stock_market_data, portfolio, update)

        # Current cash reserve is sufficient for trade volume. Trade should happen
        self.assertLess(updated_portfolio.cash, cash_reserve)
        self.assertLess(updated_portfolio.cash, portfolio.cash)
        self.assertEqual(updated_portfolio.shares[0].companyName, symbol)
        self.assertEqual(updated_portfolio.shares[0].amountOfShares, 300)


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(EvaluatorTest)
    unittest.TextTestRunner(verbosity=2).run(suite)
