from typing import List, Tuple

import datetime
from evaluating.evaluator_utils import draw, get_data_up_to_offset
from model.Portfolio import Portfolio
from model.StockMarketData import StockMarketData
from model.ITrader import ITrader
from logger import logger

PortfolioList = List[Portfolio]
TraderList = List[ITrader]
PortfolioTraderMappingList = List[Tuple[Portfolio, ITrader]]


class PortfolioEvaluator:
    """
    Given `ITrader` implementations and `StockMarketData` this evaluator watches a list of `Portfolios` over time and
    optionally demonstrates the results in a diagram
    """

    def __init__(self, trader_list: TraderList, draw_results: bool = False):
        """
        Constructor

        Args:
            trader_list: The `ITrader` implementations to use for each portfolio respectively
            draw_results: If this is set to `True` a diagram is drawn. Default: `False`
        """
        self.trader_list = trader_list
        self.draw_results = draw_results

    def inspect_over_time(self, market_data: StockMarketData, portfolios: PortfolioList, evaluation_offset: int = -1,
                          date_offset: datetime.date = None):
        """
        Lets the clock tick and executes this for every given `Portfolio` on every tick:
        * Notifies the trader which returns a list of orders
        * Apply the orders
        * Save the portfolio's state after the trade(s)

        Args:
            market_data: The stock market data with which to work. Only those symbols are tradable for that are
             contained in this data
            portfolios: The list of portfolios to manage
            evaluation_offset: How many data rows should we look backward (from the end of `market_data`) as a start
             date? If omitted all data rows will be used. Default: -1, which is equal to omitting the parameter.
            date_offset: Use a date offset instead of `evaluation_offset`. If this is set it overwrites any value
             provided as `evaluation_offset`

        Returns:
            All portfolios' value courses. If `self.draw_results` is `True`: It also draws the course of all portfolios
             given the market data
        """
        portfolio_trader_mapping = list(zip(portfolios, self.trader_list))

        return self.inspect_over_time_with_mapping(market_data, portfolio_trader_mapping, evaluation_offset,
                                                   date_offset)

    def inspect_over_time_with_mapping(self, market_data: StockMarketData,
                                       portfolio_trader_mapping: PortfolioTraderMappingList,
                                       evaluation_offset: int = -1,
                                       date_offset: datetime.date = None):
        """
        Behaves exactly as `#inspect_over_time *except* for the parameter `portfolio_trader_mapping`:
        While `#inspect_over_time` uses the traders provided to the constructor of this class, this method uses the
        provided list of trader-portfolio mappings. This allows for an fixed association between portfolios and their
        traders

        Args:
            market_data:
            portfolio_trader_mapping: A mapping between portfolios and traders.
             Structure: `List[Tuple[Portfolio, ITrader]]`
            evaluation_offset:
            date_offset:

        Returns:

        """
        # Map that holds all portfolios in the course of time. Structure: {portfolio_name => {date => portfolio}}
        all_portfolios = {}

        # Cache that holds the latest object of each portfolio. Structure: {portfolio_name => portfolio}
        portfolio_cache = {}

        if not market_data.check_data_length():
            # Checks whether all data series are of the same length (i.e. have an equal count of date->price items)
            return

        if evaluation_offset == -1 and date_offset is None:
            # `evaluation_offset` has the 'disabled' value, so we calculate it based on the underlying data
            evaluation_offset = market_data.get_row_count()

        if date_offset is not None:
            # `date_offset` is set, so the `evaluation_offset` is calculated based on the given date
            first_company = next(iter(market_data.get_companies()))
            market_data_for_company = market_data[first_company]
            index = market_data_for_company.get_dates().index(date_offset)
            evaluation_offset = market_data.get_row_count() - index

        # Reading should start one day later, because we also save the initial portfolio value in our return data.
        # Therefore the return data contains `evaluation_offset` rows which includes `evaluation_offset`-1 trades
        evaluation_offset = evaluation_offset - 1

        # And now the clock ticks
        # We start at -`evaluation_offset` and roll through the `market_data` in forward direction until the
        # second-to-last item
        for current_tick in range(-evaluation_offset, 0):

            # Retrieve the stock market data up the current day, i.e. move one tick further in `market_data`
            current_market_data = get_data_up_to_offset(market_data, current_tick)

            # Retrieve the current date
            current_date = current_market_data.get_most_recent_trade_day()

            portfolio_list = [p_t[0] for p_t in portfolio_trader_mapping]
            logger.debug(f"Start updating portfolios {portfolio_list} on {current_date} (tick {current_tick})")

            for portfolio, trader in portfolio_trader_mapping:
                if current_tick == -evaluation_offset:
                    # Save the starting state of this portfolio
                    yesterday = current_date - datetime.timedelta(days=1)
                    all_portfolios.update({portfolio.name: {yesterday: portfolio}})
                    portfolio_cache.update({portfolio.name: portfolio})

                # Retrieve latest portfolio object from cache
                portfolio_to_update = portfolio_cache[portfolio.name]

                # Determine the total portfolio value at this time
                current_total_portfolio_value = portfolio_to_update.total_value(current_date, current_market_data)

                # Ask the trader for its action
                update = trader.doTrade(portfolio_to_update, current_total_portfolio_value, current_market_data)

                # Update the portfolio that is saved at ILSE - The InnovationLab Stock Exchange ;-)
                updated_portfolio = portfolio_to_update.update(current_market_data, update)

                # Save the updated portfolio in our dict under the current date as key
                all_portfolios[updated_portfolio.name][current_date] = updated_portfolio
                portfolio_cache.update({portfolio.name: updated_portfolio})

            logger.debug(f"End updating portfolios {portfolio_list} on {current_date} (tick {current_tick})\n")

        # Draw a diagram of the portfolios' changes over time - if we're not unit testing
        if self.draw_results:
            draw(all_portfolios, market_data)

        return all_portfolios
