from typing import List

from evaluating.evaluator import draw, get_data_up_to_offset, check_data_length
from trading.trader_interface import ITrader, StockMarketData, Portfolio

PortfolioList = List[Portfolio]


class PortfolioEvaluator:
    """
    Given an `ITrader` implementation and `StockMarketData` this evaluator watches a list of `Portfolios` over time
    """

    def __init__(self, trader: ITrader = None):
        """
        Constructor
        """
        self.trader = trader

    def inspect_over_time(self, evaluation_offset: int, market_data: StockMarketData, portfolios: PortfolioList):
        """

        :param evaluation_offset: How many data rows should we look backward (from the end of `market_data`) as a start
        date?
        :param market_data: The stock market data with which to work. Only those symbols are tradable for that are
        contained in this data
        :param portfolios: The list of portfolios to manage
        :return: Nothing. It just draws the course of all portfolios given the market data
        """
        all_portfolios = {}

        if not check_data_length(market_data):
            # Checks whether all data series are of the same length (i.e. have an equal count of date->price items)
            return

        for portfolio in portfolios:
            portfolio_over_time = {}
            all_portfolios[portfolio.name] = portfolio_over_time

            # Save the starting state of this portfolio
            portfolio_over_time[next(iter(market_data.market_data.values()))[-evaluation_offset][0]] = portfolio

            # And now the clock ticks: We start at `offset - 1` and roll through the `market_data` in forward direction
            for index in range(evaluation_offset - 1):
                current_tick = index - evaluation_offset - 1

                # Retrieve the stock market data up the current day, i.e. move one tick further in `market_data`
                current_market_data = get_data_up_to_offset(market_data, current_tick)

                # Retrieve the current date and the total portfolio value at this time
                current_date = current_market_data.get_most_recent_trade_day()
                current_total_portfolio_value = portfolio.total_value(current_date, current_market_data.market_data)

                # Ask the trader for its action
                update = self.trader.doTrade(portfolio, current_total_portfolio_value, current_market_data,
                                             *current_market_data.market_data.keys())

                # Update the portfolio that is saved at ILSE - The InnovationLab Stock Exchange ;-)
                portfolio = portfolio.update(current_market_data, update)

                # Save the updated portfolio in our dict under the current date as key
                portfolio_over_time[current_date] = portfolio

        # Draw a diagram of the portfolios' changes over time
        draw(all_portfolios, current_market_data)
