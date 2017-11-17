# Start evaluation rnn_trader:
# Compare its performance over the testing period (2012-2017) against a buy-and-hold trader.
from utils import read_stock_market_data_conveniently
from evaluating.portfolio_evaluator import PortfolioEvaluator
from model.CompanyEnum import CompanyEnum
from model.Portfolio import Portfolio
from predicting.predictor.perfect_predictor import PerfectPredictor
from trading.trader.buy_and_hold_trader import BuyAndHoldTrader
from trading.trader.rnn_trader import RnnTrader

if __name__ == "__main__":
    # Load stock market data for training and testing period
    training_period, testing_period = '1962-2011', '2012-2017'
    stock_market_data = read_stock_market_data_conveniently([CompanyEnum.COMPANY_A, CompanyEnum.COMPANY_B],
                                                            [training_period, testing_period])

    # Define benchmark and trader
    benchmark = BuyAndHoldTrader()
    trader = RnnTrader(PerfectPredictor(CompanyEnum.COMPANY_A), PerfectPredictor(CompanyEnum.COMPANY_B), False)

    # Define identical portfolio for benchmark and trader
    benchmark_portfolio = Portfolio(10000, [], 'Benchmark')
    trader_portfolio = Portfolio(10000, [], 'RNN Trader')

    # Evaluate their performance over the testing period
    evaluator = PortfolioEvaluator([benchmark, trader], True)
    # TODO @jonas ich möchte über die testing_period testen, muss hier aber manuell einen offset in Tagen berechnen
    # TODO kriegen wir das eleganter hin?
    stock_data_testing_period = read_stock_market_data_conveniently([CompanyEnum.COMPANY_A], [testing_period])
    days_of_testing_period = len(stock_data_testing_period.get_stock_data_for_company(CompanyEnum.COMPANY_A))
    evaluator.inspect_over_time(stock_market_data, [benchmark_portfolio, trader_portfolio], days_of_testing_period)
