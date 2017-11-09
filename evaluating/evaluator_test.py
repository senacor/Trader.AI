'''
Created on 08.11.2017

Module for testing of the evaluating component

@author: jholtkamp
'''
import unittest

from evaluating.evaluator import read_portfolio, read_stock_market_data, update_portfolio
from trading.simple_trader import SimpleTrader
from trading.trader_interface import CompanyEnum, TradingAction, TradingActionEnum, SharesOfCompany, Portfolio


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
        stock_market_data = read_stock_market_data()

        self.assertGreater(len(stock_market_data.companyName2DateValueArrayDict), 0)
        self.assertTrue(stock_market_data.companyName2DateValueArrayDict.__contains__(CompanyEnum.APPLE.value))

    def testDoTrade(self):
        portfolio = read_portfolio()

        trading_action = SimpleTrader().doTrade(portfolio, read_stock_market_data())

        if trading_action is not None:
            self.assertEqual(trading_action.sharesOfCompany.companyName, CompanyEnum.APPLE.value)

    def testUpdatePortfolio(self):
        cash_reserve = 10000.0

        portfolio = Portfolio(cash_reserve, [SharesOfCompany('AAPL', 200)])
        update = TradingAction(TradingActionEnum.BUY, SharesOfCompany('AAPL', 100))
        update_portfolio(read_stock_market_data(), portfolio, update)

        # Trade volume is too high for current cash reserve. Nothing should happen
        self.assertEqual(portfolio.cash, cash_reserve)


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(EvaluatorTest)
    unittest.TextTestRunner(verbosity=2).run(suite)
