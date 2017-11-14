from typing import List

import datetime

from evaluating.evaluator import draw, get_data_up_to_offset, check_data_length
from trading.trader_interface import ITrader, StockMarketData, Portfolio

PortfolioList = List[Portfolio]


class PortfolioEvaluator:
    """
    Given an `ITrader` implementation and `StockMarketData` this evaluator watches a list of `Portfolios` over time
    """

    def __init__(self, trader: ITrader = None, draw_results: bool = False):
        """
        Constructor
        :param trader: The `ITrader` implementation to use
        :param draw_results: If this is set to `False` a diagram is *not* drawn
        """
        self.trader = trader
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

        # Map that holds all portfolios in the course of time. Structure: {portfolio_name => {date => portfolio}}
        all_portfolios = {}

        # Cache that holds the latest object of each portfolio. Structure: {portfolio_name => portfolio}
        portfolio_cache = {}

        if not check_data_length(market_data):
            # Checks whether all data series are of the same length (i.e. have an equal count of date->price items)
            return

        # And now the clock ticks: We start at `offset - 1` and roll through the `market_data` in forward direction
        for index in range(evaluation_offset - 1):
            current_tick = index - evaluation_offset - 1

            # Retrieve the stock market data up the current day, i.e. move one tick further in `market_data`
            current_market_data = get_data_up_to_offset(market_data, current_tick)

            # Retrieve the current date
            current_date = current_market_data.get_most_recent_trade_day()

            for portfolio in portfolios:
                if index == 0:
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
                update = self.trader.doTrade(portfolio_to_update, current_total_portfolio_value, current_market_data,
                                             *current_market_data.market_data.keys())

                # Update the portfolio that is saved at ILSE - The InnovationLab Stock Exchange ;-)
                updated_portfolio = portfolio_to_update.update(current_market_data, update)

                # Save the updated portfolio in our dict under the current date as key
                all_portfolios[updated_portfolio.name][current_date] = updated_portfolio
                portfolio_cache.update({portfolio.name: updated_portfolio})

        # Draw a diagram of the portfolios' changes over time - if we're not unit testing
        if not self.draw_results:
            draw(all_portfolios, market_data)

        return all_portfolios
