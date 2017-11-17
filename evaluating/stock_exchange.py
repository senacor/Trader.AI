# Start evaluation rnn_trader:
# Compare its performance over the testing period (2012-2017) against a buy-and-hold trader.
from trading.trader.simple_trader import SimpleTrader
from utils import read_stock_market_data
from evaluating.portfolio_evaluator import PortfolioEvaluator
from model.CompanyEnum import CompanyEnum
from model.Portfolio import Portfolio
from predicting.predictor.perfect_predictor import PerfectPredictor
from trading.trader.buy_and_hold_trader import BuyAndHoldTrader
from trading.trader.rnn_trader import RnnTrader

if __name__ == "__main__":
    # Load stock market data for training and testing period
    training_period, testing_period = '1962-2011', '2012-2017'
    stock_market_data = read_stock_market_data([CompanyEnum.COMPANY_A, CompanyEnum.COMPANY_B],
                                               [training_period, testing_period])

    # Define traders
    buy_and_hold_trader = BuyAndHoldTrader()
    simple_trader = SimpleTrader(PerfectPredictor(CompanyEnum.COMPANY_A), PerfectPredictor(CompanyEnum.COMPANY_B))
    rnn_trader = RnnTrader(PerfectPredictor(CompanyEnum.COMPANY_A), PerfectPredictor(CompanyEnum.COMPANY_B), False)

    # Define portfolios for the traders
    benchmark_portfolio = Portfolio(10000, [], 'BuyAndHoldTrader')
    simple_trader_portfolio = Portfolio(10000, [], 'SimpleTrader')
    rnn_trader_portfolio = Portfolio(10000, [], 'RnnTrader')

    # Evaluate their performance over the testing period
    evaluator = PortfolioEvaluator([buy_and_hold_trader, simple_trader, rnn_trader], True)
    # TODO @jonas ich möchte über die testing_period testen, muss hier aber manuell einen offset in Tagen berechnen
    # TODO kriegen wir das eleganter hin?
    stock_data_testing_period = read_stock_market_data([CompanyEnum.COMPANY_A], [testing_period])
    days_of_testing_period = len(stock_data_testing_period.get_stock_data_for_company(CompanyEnum.COMPANY_A))
    evaluator.inspect_over_time(stock_market_data, [benchmark_portfolio, simple_trader_portfolio, rnn_trader_portfolio], 100)
