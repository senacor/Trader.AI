# Start evaluation traders:
# Compare their performance over the testing period (2012-2017) against a buy-and-hold trader.
from evaluating.evaluator_utils import initialize_portfolios
from utils import read_stock_market_data
from evaluating.portfolio_evaluator import PortfolioEvaluator
from model.CompanyEnum import CompanyEnum
from dependency_injection_containers import Traders
import datetime
from definitions import PERIOD_1, PERIOD_2

if __name__ == "__main__":
    # Load stock market data for training and testing period
    stock_market_data = read_stock_market_data([CompanyEnum.COMPANY_A, CompanyEnum.COMPANY_B], [PERIOD_1, PERIOD_2])

    # Define portfolio-name/trader mappings
    portfolio_name_trader_mappings = [
        # Benchmark trader
        ('Buy-and-hold Trader', Traders.BuyAndHoldTrader()),

        # Simple traders
        ('Simple Trader (perfect prediction)', Traders.SimpleTrader_with_perfect_prediction()),
        ('Simple Trader (NN binary perfect prediction)', Traders.SimpleTrader_with_nn_binary_perfect_prediction()),
        ('Simple Trader (NN binary prediction)', Traders.SimpleTrader_with_nn_binary_prediction()),

        # Deep Q-Learning traders
        ('DQL Trader (perfect_prediction)', Traders.DqlTrader_with_perfect_prediction()),
        ('DQL Trader (NN binary perfect prediction)', Traders.DqlTrader_with_nn_binary_perfect_prediction()),
        ('DQL Trader (NN binary prediction))', Traders.DqlTrader_with_nn_binary_prediction()),
    ]

    # Define portfolios for the traders and create a portfolio/trader mapping
    portfolio_trader_mappings = initialize_portfolios(10000.0, portfolio_name_trader_mappings)

    # Evaluate their performance over the testing period
    evaluator = PortfolioEvaluator([], True)
    evaluator.inspect_over_time_with_mapping(stock_market_data, portfolio_trader_mappings,
                                             date_offset=datetime.date(2012, 1, 3))
