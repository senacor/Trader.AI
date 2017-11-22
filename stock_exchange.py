# Start evaluation rnn_trader:
# Compare its performance over the testing period (2012-2017) against a buy-and-hold trader.
from trading.trader.simple_trader import SimpleTrader
from utils import read_stock_market_data
from evaluating.portfolio_evaluator import PortfolioEvaluator
from model.CompanyEnum import CompanyEnum
from model.Portfolio import Portfolio
from predicting.predictor.perfect_predictor import PerfectPredictor
from trading.trader.buy_and_hold_trader import BuyAndHoldTrader
from trading.trader.dql_trader import DqlTrader
from dependency_injection_containers import Traders

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
    #evaluator = PortfolioEvaluator([buy_and_hold_trader, dql_trader], True)
    # TODO @jonas ich möchte über die testing_period testen, muss hier aber manuell einen offset in Tagen berechnen
    # TODO kriegen wir das eleganter hin?
    # TODO @Richard Accomplished it by adding a parameter `date_offset`. Watch it being in action in
    # TODO `EvaluatorTest#test_inspect_with_date_offset` (jh)
    stock_data_testing_period = read_stock_market_data([CompanyEnum.COMPANY_A], [testing_period])
    days_of_testing_period = stock_data_testing_period.get_for_company(CompanyEnum.COMPANY_A).get_row_count()
    evaluator.inspect_over_time(stock_market_data, [benchmark_portfolio, 
                                                    simple_trader_with_perfect_prediction_portfolio, 
                                                    simple_trader_with_nn_binary_perfect_prediction_portfolio,
                                                    simple_trader_with_nn_binary_prediction_portfolio,
                                                    dql_trader_with_perfect_prediction_portfolio,
                                                    dql_trader_with_nn_binary_perfect_prediction_portfolio,
                                                    dql_trader_with_nn_binary_prediction_portfolio], 400)
