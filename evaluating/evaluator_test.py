'''
Created on 08.11.2017

Module for testing of the evaluating component

@author: jholtkamp
'''
import unittest

from evaluating.evaluator import read_portfolio, read_stock_market_data, update_portfolio, draw
from predicting.simple_predictor import SimplePredictor
from trading.simple_trader import SimpleTrader
from trading.trader_interface import CompanyEnum, TradingAction, TradingActionEnum, SharesOfCompany, Portfolio, \
    StockMarketData


def getMarketData(symbol: str, stock_market_data: StockMarketData, offset: int):
    if offset == 0: return stock_market_data
    return StockMarketData({symbol: stock_market_data.market_data[symbol].copy()[:offset]})


def get_current_date(symbol: str, stock_market_data: StockMarketData):
    return stock_market_data.market_data[symbol][-1][0]


class EvaluatorTest(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testReadPortfolio(self):
        portfolio = read_portfolio()

        self.assertEqual(len(portfolio.shares), 2)
        self.assertEqual(portfolio.cash, 10000.0)
        self.assertEqual(portfolio.shares[0].name, CompanyEnum.GOOGLE.value)

    def testReadStockMarketData(self):
        apple = CompanyEnum.APPLE.value
        google = CompanyEnum.GOOGLE.value

        stock_market_data = read_stock_market_data([apple, google])

        self.assertGreater(len(stock_market_data.market_data), 0)
        self.assertTrue(apple in stock_market_data.market_data)
        self.assertTrue(google in stock_market_data.market_data)

    def testDoTrade(self):
        apple = CompanyEnum.APPLE.value

        trading_action = SimpleTrader().doTrade(read_portfolio(), read_stock_market_data([apple]))

        self.assertTrue(trading_action is not None)
        self.assertEqual(trading_action.shares.name, apple)

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
        self.assertEqual(updated_portfolio.shares[0].name, symbol)
        self.assertEqual(updated_portfolio.shares[0].amount, 200)

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
        self.assertEqual(updated_portfolio.shares[0].name, symbol)
        self.assertEqual(updated_portfolio.shares[0].amount, 300)

    def testUpdateAndDraw(self):
        symbol = 'stock_a'
        trader = SimpleTrader(SimplePredictor())

        # Reading in *all* available data
        data1 = read_stock_market_data(['stock_a_1962-2011'])
        data2 = read_stock_market_data(['stock_a_2012-2017'])

        # Combine both datasets to one StockMarketData object
        old_data = data1.market_data['stock_a_1962-2011']
        new_data = data2.market_data['stock_a_2012-2017']
        full_stock_market_data = StockMarketData({symbol: old_data + new_data})

        portfolio_over_time = {}
        count_of_new_market_data = len(new_data) - 1

        # Calculate and save the initial total portfolio value (i.e. the cash reserve)
        portfolio = Portfolio(50000.0, [])
        portfolio_over_time[new_data[0][0]] = portfolio

        print(portfolio_over_time)

        for index in range(count_of_new_market_data):
            currentTick = index - count_of_new_market_data

            # Retrieve the stock market data up the current day
            stock_market_data = getMarketData(symbol, full_stock_market_data, currentTick)

            # Ask the trader for its action
            update = trader.doTrade(portfolio, stock_market_data)

            # Update the portfolio that is saved at the ILSE
            portfolio = update_portfolio(stock_market_data, portfolio, update)

            # Save the updated portfolio in our dict
            portfolio_over_time[get_current_date(symbol, stock_market_data)] = portfolio

        # Draw a diagram of the portfolio's changes over time
        draw(portfolio_over_time, stock_market_data)


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(EvaluatorTest)
    unittest.TextTestRunner(verbosity=2).run(suite)
