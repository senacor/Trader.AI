"""
Created on 08.11.2017

Module for testing of the evaluating component

@author: Jonas Holtkamp
"""
import unittest

from evaluating.evaluator import read_portfolio, read_stock_market_data
from predicting.simple_predictor import SimplePredictor
from predicting.perfect_stock_a_predictor import PerfectStockAPredictor
from trading.simple_trader import SimpleTrader
from trading.trader_interface import CompanyEnum, TradingAction, TradingActionEnum, SharesOfCompany, StockMarketData, \
    TradingActionList, Portfolio


class EvaluatorTest(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testReadPortfolio(self):
        portfolio = read_portfolio()

        self.assertEqual(len(portfolio.shares), 2)
        self.assertEqual(portfolio.cash, 10000.0)
        self.assertEqual(portfolio.shares[0].name, 'GOOG')

    def testReadStockMarketData(self):
        apple = 'AAPL'
        google = 'GOOG'

        stock_market_data = read_stock_market_data([apple, google])

        self.assertGreater(len(stock_market_data.market_data), 0)
        self.assertTrue(apple in stock_market_data.market_data)
        self.assertTrue(google in stock_market_data.market_data)

    def testGetMostRecentTradeDay(self):
        apple = 'AAPL'
        google = 'GOOG'

        stock_market_data = read_stock_market_data([apple, google])

        self.assertEqual(stock_market_data.get_most_recent_trade_day(), stock_market_data.market_data[apple][-1][0])

    def testDoTrade(self):
        symbol = 'AAPL'

        trader = SimpleTrader(PerfectStockAPredictor(), None)
        current_portfolio_value = 0.0  # Dummy value
        trading_action_list = trader.doTrade(read_portfolio(), current_portfolio_value,
                                             read_stock_market_data([symbol]), company_a_name=symbol)

        self.assertTrue(trading_action_list is not None)
        self.assertTrue(trading_action_list.len(), 1)
        self.assertEqual(trading_action_list.get(0).shares.name, symbol)

    def testUpdatePortfolio_noSufficientCashReserve(self):
        cash_reserve = 10000.0
        symbol = CompanyEnum.COMPANY_A.value

        data = list()
        data.append(('2017-01-01', 150.0))
        stock_market_data = StockMarketData({symbol: data})

        portfolio = Portfolio(cash_reserve, [SharesOfCompany(symbol, 200)])
        trading_action_list = TradingActionList()
        trading_action_list.addTradingAction(TradingAction(TradingActionEnum.BUY, SharesOfCompany(symbol, 100)))

        updated_portfolio = portfolio.update(stock_market_data, trading_action_list)

        # Trade volume is too high for current cash reserve. Nothing should happen
        self.assertEqual(updated_portfolio.cash, cash_reserve)
        self.assertEqual(updated_portfolio.cash, portfolio.cash)
        self.assertEqual(updated_portfolio.shares[0].name, symbol)
        self.assertEqual(updated_portfolio.shares[0].amount, 200)

    def testUpdatePortfolio_sufficientCashReserve(self):
        cash_reserve = 20000.0
        symbol = CompanyEnum.COMPANY_A.value

        data = list()
        data.append(('2017-01-01', 150.0))
        stock_market_data = StockMarketData({symbol: data})

        portfolio = Portfolio(cash_reserve, [SharesOfCompany(symbol, 200)])

        trading_action_list = TradingActionList()
        trading_action_list.addTradingAction(TradingAction(TradingActionEnum.BUY, SharesOfCompany(symbol, 100)))

        updated_portfolio = portfolio.update(stock_market_data, trading_action_list)

        # Current cash reserve is sufficient for trade volume. Trade should happen
        self.assertLess(updated_portfolio.cash, cash_reserve)
        self.assertLess(updated_portfolio.cash, portfolio.cash)
        self.assertEqual(updated_portfolio.shares[0].name, symbol)
        self.assertEqual(updated_portfolio.shares[0].amount, 300)

    def testUpdateAndDraw(self):
        trader = SimpleTrader(SimplePredictor(), SimplePredictor())

        from evaluating.portfolio_evaluator import PortfolioEvaluator
        evaluator = PortfolioEvaluator(trader)

        period1 = '1962-2011'
        period2 = '2012-2017'

        stock_a = 'stock_a'
        stock_b = 'stock_b'

        # Reading in *all* available data
        data_a1 = read_stock_market_data([('%s_%s' % (stock_a, period1))])
        data_a2 = read_stock_market_data([('%s_%s' % (stock_a, period2))])

        data_b1 = read_stock_market_data([('%s_%s' % (stock_b, period1))])
        data_b2 = read_stock_market_data([('%s_%s' % (stock_b, period2))])

        # Combine both datasets to one StockMarketData object
        old_data_a = data_a1.market_data[('%s_%s' % (stock_a, period1))]
        new_data_a = data_a2.market_data[('%s_%s' % (stock_a, period2))]

        old_data_b = data_b1.market_data[('%s_%s' % (stock_b, period1))]
        new_data_b = data_b2.market_data[('%s_%s' % (stock_b, period2))]

        full_stock_market_data = StockMarketData({stock_a: old_data_a + new_data_a, stock_b: old_data_b + new_data_b})

        # Calculate and save the initial total portfolio value (i.e. the cash reserve)
        portfolio1 = Portfolio(50000.0, [], 'portfolio 1')
        portfolio2 = Portfolio(100000.0, [], 'portfolio 2')
        portfolio3 = Portfolio(150000.0, [], 'portfolio 3')

        evaluator.inspect_over_time(200, full_stock_market_data, [portfolio1, portfolio2, portfolio3])


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(EvaluatorTest)
    unittest.TextTestRunner(verbosity=2).run(suite)
