# Start evaluation rnn_trader:
# Compare its performance over the testing period (2012-2017) against a buy-and-hold trader.
from definitions import DATASETS_DIR
from evaluating.evaluator_utils import read_stock_market_data
from evaluating.portfolio_evaluator import PortfolioEvaluator
from model.Portfolio import Portfolio
from model.StockMarketData import StockMarketData
from model.CompanyEnum import CompanyEnum
from predicting.perfect_stock_a_predictor import PerfectStockAPredictor
from trading.rnn_trader import RnnTrader

if __name__ == "__main__":
    # TODO @Jonas Kann man das Laden der Daten auslagern?
    stock_a = 'stock_a'
    stock_b = 'stock_b'
    period1 = '1962-2011'
    period2 = '2012-2017'
    # Reading in *all* available data
    data_a1 = read_stock_market_data([[CompanyEnum.COMPANY_A, ('%s_%s' % (stock_a, period1))]], DATASETS_DIR)
    data_a2 = read_stock_market_data([[CompanyEnum.COMPANY_A, ('%s_%s' % (stock_a, period2))]], DATASETS_DIR)
    data_b1 = read_stock_market_data([[CompanyEnum.COMPANY_B, ('%s_%s' % (stock_b, period1))]], DATASETS_DIR)
    data_b2 = read_stock_market_data([[CompanyEnum.COMPANY_B, ('%s_%s' % (stock_b, period2))]], DATASETS_DIR)
    # Combine both datasets to one StockMarketData object
    old_data_a = data_a1.market_data[CompanyEnum.COMPANY_A]
    new_data_a = data_a2.market_data[CompanyEnum.COMPANY_A]
    old_data_b = data_b1.market_data[CompanyEnum.COMPANY_B]
    new_data_b = data_b2.market_data[CompanyEnum.COMPANY_B]
    full_stock_market_data = StockMarketData({stock_a: old_data_a + new_data_a, stock_b: old_data_b + new_data_b})

    # TODO @Jonas Kann man dieses Benchmark hier eleganter machen, z.B. dependency injection?
    benchmark = BuyAndHoldTrader()
    trader_under_test = RnnTrader(PerfectStockAPredictor(),
                                  PerfectStockAPredictor())  # TODO implement PerfectStockBPredictor
    benchmark_portfolio = Portfolio(10000, [], 'Benchmark')
    trader_under_test_portfolio = Portfolio(10000, [], 'RNN Trader')
    evaluator = PortfolioEvaluator([benchmark, trader_under_test], True)
    evaluator.inspect_over_time(full_stock_market_data, [benchmark_portfolio, trader_under_test_portfolio], 1000)