from typing import List

import datetime

from definitions import DATASETS_DIR

from evaluating.evaluator import draw, get_data_up_to_offset, check_data_length, read_stock_market_data
from predicting.perfect_stock_a_predictor import PerfectStockAPredictor
from trading.buy_and_hold_trader import BuyAndHoldTrader
from trading.rnn_trader import RnnTrader
from trading.trader_interface import ITrader, StockMarketData, Portfolio, CompanyEnum

PortfolioList = List[Portfolio]
TraderList = List[ITrader]


class PortfolioEvaluator:
    """
    Given an `ITrader` implementation and `StockMarketData` this evaluator watches a list of `Portfolios` over time
    """

    def __init__(self, trader_list: TraderList, draw_results: bool = False):
        """
        Constructor
        :param trader: The `ITrader` implementation to use
        :param draw_results: If this is set to `False` a diagram is *not* drawn
        """
        self.trader_list = trader_list
        self.draw_results = draw_results

    def inspect_over_time(self, market_data: StockMarketData, portfolios: PortfolioList, evaluation_offset: int = -1):
        """
        Lets the clock tick and executes this for every given `Portfolio` on every tick:
        * Notifies the trader which returns a list of trading actions
        * Apply the trading actions
        * Save the portfolio's state after the trade(s)

        :param market_data: The stock market data with which to work. Only those symbols are tradable for that are
        contained in this data
        :param portfolios: The list of portfolios to manage
        :param evaluation_offset: How many data rows should we look backward (from the end of `market_data`) as a start
        date? If omitted all data rows will be used. Default: -1, which is equal to omitting the parameter
        :return: If `self.test_mode` is `True`: All portfolios' value courses. Otherwise: Nothing. It just draws the
        course of all portfolios given the market data
        """

        portfolio_trader_mapping = list(zip(portfolios, self.trader_list))

        # Map that holds all portfolios in the course of time. Structure: {portfolio_name => {date => portfolio}}
        all_portfolios = {}

        # Cache that holds the latest object of each portfolio. Structure: {portfolio_name => portfolio}
        portfolio_cache = {}

        if not check_data_length(market_data):
            # Checks whether all data series are of the same length (i.e. have an equal count of date->price items)
            return

        if evaluation_offset == -1:
            # `evaluation_offset` has the 'disabled' value, so we calculate it based on the underlying data
            evaluation_offset = market_data.get_row_count() - 1

        # And now the clock ticks
        for index in range(1, evaluation_offset):
            # We start at -`evaluation_offset` and roll through the `market_data` in forward direction
            current_tick = index - evaluation_offset + 1

            # Retrieve the stock market data up the current day, i.e. move one tick further in `market_data`
            current_market_data = get_data_up_to_offset(market_data, current_tick)

            # Retrieve the current date
            current_date = current_market_data.get_most_recent_trade_day()

            for portfolio, trader in portfolio_trader_mapping:
                if index == 1:
                    # Save the starting state of this portfolio
                    yesterday = current_date - datetime.timedelta(days=1)
                    all_portfolios.update({portfolio.name: {yesterday: portfolio}})
                    portfolio_cache.update({portfolio.name: portfolio})

                # Retrieve latest portfolio object from cache
                portfolio_to_update = portfolio_cache[portfolio.name]

                # Determine the total portfolio value at this time
                current_total_portfolio_value = portfolio_to_update.total_value(current_date,
                                                                                current_market_data.market_data)

                # Ask the trader for its action
                update = trader.doTrade(portfolio_to_update, current_total_portfolio_value, current_market_data)

                # Update the portfolio that is saved at ILSE - The InnovationLab Stock Exchange ;-)
                updated_portfolio = portfolio_to_update.update(current_market_data, update)

                # Save the updated portfolio in our dict under the current date as key
                all_portfolios[updated_portfolio.name][current_date] = updated_portfolio
                portfolio_cache.update({portfolio.name: updated_portfolio})

        # Draw a diagram of the portfolios' changes over time - if we're not unit testing
        if self.draw_results:
            draw(all_portfolios, market_data)

        return all_portfolios

# Start evaluation rnn_trader:
# Compare its performance over the testing period (2012-2017) against a buy-and-hold trader.
if __name__ == "__main__":
    # TODO @Jonas Kann man das Laden der Daten auslagern?
    stock_a = 'stock_a'
    stock_b = 'stock_b'
    period1 = '1962-2011'
    period2 = '2012-2017'
    # Reading in *all* available data
    data_a1 = read_stock_market_data([[CompanyEnum.COMPANY_A.value, ('%s_%s' % (stock_a, period1))]], DATASETS_DIR)
    data_a2 = read_stock_market_data([[CompanyEnum.COMPANY_A.value, ('%s_%s' % (stock_a, period2))]], DATASETS_DIR)
    data_b1 = read_stock_market_data([[CompanyEnum.COMPANY_B.value, ('%s_%s' % (stock_b, period1))]], DATASETS_DIR)
    data_b2 = read_stock_market_data([[CompanyEnum.COMPANY_B.value, ('%s_%s' % (stock_b, period2))]], DATASETS_DIR)
    # Combine both datasets to one StockMarketData object
    old_data_a = data_a1.market_data[CompanyEnum.COMPANY_A.value]
    new_data_a = data_a2.market_data[CompanyEnum.COMPANY_A.value]
    old_data_b = data_b1.market_data[CompanyEnum.COMPANY_B.value]
    new_data_b = data_b2.market_data[CompanyEnum.COMPANY_B.value]
    full_stock_market_data = StockMarketData({stock_a: old_data_a + new_data_a, stock_b: old_data_b + new_data_b})

    # TODO @Jonas Kann man dieses Benchmark hier eleganter machen, z.B. dependency injection?
    benchmark = BuyAndHoldTrader()
    trader_under_test = RnnTrader(PerfectStockAPredictor(), PerfectStockAPredictor())  # TODO implement PerfectStockBPredictor
    benchmark_portfolio = Portfolio(10000, [], 'Benchmark')
    trader_under_test_portfolio = Portfolio(10000, [], 'RNN Trader')
    evaluator = PortfolioEvaluator([benchmark, trader_under_test], True)
    evaluator.inspect_over_time(full_stock_market_data, [benchmark_portfolio, trader_under_test_portfolio], 1000)