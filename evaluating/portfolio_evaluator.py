from typing import List

from evaluating.evaluator import update_portfolio, draw
from trading.trader_interface import ITrader, Portfolio, StockMarketData, CompanyEnum

PortfolioList = List[Portfolio]


class PortfolioEvaluator:
    '''
    Simple Trader generates TradingAction based on simple logic, input data and prediction from NN-Engine
    '''

    def __init__(self, trader: ITrader = None):
        '''
        Constructor
        '''
        self.trader = trader

    #TODO Convention: Camel case for variables and function/method names
    def inspect_over_time(self, evaluation_offset: int, market_data: StockMarketData, portfolios: PortfolioList):
        all_portfolios = {}

        if not self.check_data_length(market_data):
            # Checks whether all data series are of the same length (i.e. have equal date->price items)
            return

        for portfolio in portfolios:
            portfolio_over_time = {}
            all_portfolios[portfolio.name] = portfolio_over_time

            portfolio_over_time[next(iter(market_data.market_data.values()))[-evaluation_offset][0]] = portfolio
            print(portfolio_over_time)

            for index in range(evaluation_offset - 1):
                current_tick = index - evaluation_offset - 1

                # Retrieve the stock market data up the current day
                stock_market_data = self.get_data_up_to_offset(market_data, current_tick)

                # Ask the trader for its action
                #TODO -> current date should be independent from company name! 
                #TODO -> Use Constants or Enums - no magic values or strings
                currentDate = stock_market_data.get_most_recent_trade_day('stock_a')
                currentTotalPortfolioValue = portfolio.total_value(currentDate, stock_market_data.market_data)
                
                update = self.trader.doTrade(portfolio, currentTotalPortfolioValue, stock_market_data, 'stock_a', 'stock_b')

                # Update the portfolio that is saved at the ILSE
                portfolio = update_portfolio(stock_market_data, portfolio, update)

                # Save the updated portfolio in our dict
                portfolio_over_time[stock_market_data.market_data['stock_a'][-1][0]] = portfolio

        # Draw a diagram of the portfolios' changes over time
        draw(all_portfolios, stock_market_data)

    def get_data_up_to_offset(self, stock_market_data: StockMarketData, offset: int):
        if offset == 0: return stock_market_data

        offset_data = {}
        for key, value in stock_market_data.market_data.items():
            offset_data[key] = value.copy()[:offset]

        return StockMarketData(offset_data)

    def check_data_length(self, market_data):
        return len(set([len(key) for key in market_data.market_data.keys()])) == 1
