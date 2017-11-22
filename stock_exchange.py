# Start evaluation traders:
# Compare their performance over the testing period (2012-2017) against a buy-and-hold trader.
from utils import read_stock_market_data
from evaluating.portfolio_evaluator import PortfolioEvaluator
from model.CompanyEnum import CompanyEnum
from model.Portfolio import Portfolio
from dependency_injection_containers import Traders
import datetime

if __name__ == "__main__":
    # Load stock market data for training and testing period
    training_period, testing_period = '1962-2011', '2012-2017'
    stock_market_data = read_stock_market_data([CompanyEnum.COMPANY_A, CompanyEnum.COMPANY_B],
                                               [training_period, testing_period])

    # Define traders
    buy_and_hold_trader = Traders.BuyAndHoldTrader()

    simple_trader_with_perfect_prediction = Traders.SimpleTrader_with_perfect_prediction()
    simple_trader_with_nn_binary_perfect_prediction = Traders.SimpleTrader_with_nn_binary_perfect_prediction()
    simple_trader_with_nn_binary_prediction = Traders.SimpleTrader_with_nn_binary_prediction()

    dql_trader_with_perfect_prediction = Traders.DqlTrader_with_perfect_prediction()
    dql_trader_with_nn_binary_perfect_prediction = Traders.DqlTrader_with_nn_binary_perfect_prediction()
    dql_trader_with_nn_binary_prediction = Traders.DqlTrader_with_nn_binary_prediction()

    # Define portfolios for the traders
    benchmark_portfolio = Portfolio(10000, [], 'BuyAndHoldTrader')
    
    simple_trader_with_perfect_prediction_portfolio = Portfolio(10000, [], 'SimpleTrader_with_perfect_prediction')
    simple_trader_with_nn_binary_perfect_prediction_portfolio = Portfolio(10000, [], 'SimpleTrader_with_nn_binary_perfect_prediction')
    simple_trader_with_nn_binary_prediction_portfolio = Portfolio(10000, [], 'SimpleTrader_with_nn_binary_prediction')
    
    dql_trader_with_perfect_prediction_portfolio = Portfolio(10000, [], 'DqlTrader_with_perfect_prediction')
    dql_trader_with_nn_binary_perfect_prediction_portfolio = Portfolio(10000, [], 'DqlTrader_with_nn_binary_perfect_prediction')
    dql_trader_with_nn_binary_prediction_portfolio = Portfolio(10000, [], 'DqlTrader_with_nn_binary_prediction')

    # Evaluate their performance over the testing period
    evaluator = PortfolioEvaluator([buy_and_hold_trader,
                                    simple_trader_with_perfect_prediction, 
                                    simple_trader_with_nn_binary_perfect_prediction,
                                    simple_trader_with_nn_binary_prediction,
                                    dql_trader_with_perfect_prediction,
                                    dql_trader_with_nn_binary_perfect_prediction,
                                    dql_trader_with_nn_binary_prediction], True)
    evaluator.inspect_over_time(stock_market_data, [benchmark_portfolio, 
                                                    simple_trader_with_perfect_prediction_portfolio, 
                                                    simple_trader_with_nn_binary_perfect_prediction_portfolio,
                                                    simple_trader_with_nn_binary_prediction_portfolio,
                                                    dql_trader_with_perfect_prediction_portfolio,
                                                    dql_trader_with_nn_binary_perfect_prediction_portfolio,
                                                    dql_trader_with_nn_binary_prediction_portfolio],
                                date_offset=datetime.date(2012, 1, 3))
