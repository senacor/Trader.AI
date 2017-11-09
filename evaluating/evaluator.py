import json
import numpy

import Columns
from trading.trader_interface import Portfolio, SharesOfCompany, StockMarketData, TradingAction, TradingActionEnum


def read_portfolio(name: str = 'portfolio') -> Portfolio:
    file = open("../json/" + name + ".json")
    json_data = file.read()
    data = json.loads(json_data)
    file.close()

    shares_list = list()
    for share in data['shares']:
        shares_list.append(SharesOfCompany(share['name'], share['amount']))

    # pprint(shares_list[0].companyName)
    # pprint(shares_list[0].amountOfShares)
    # pprint(data['cash'])
    return Portfolio(data['cash'], shares_list)


def read_stock_market_data(name: str = 'AAPL', path: str = '../datasets/') -> StockMarketData:
    na_portfolio = numpy.loadtxt(path + name + '.csv', dtype='|S15,f8,f8,f8,f8,f8,i8',
                                 delimiter=',', comments="#", skiprows=1)
    alist = list()
    for day in na_portfolio:
        alist.append((day[Columns.DATE], day[Columns.ADJ_CLOSE]))

    data = {name: alist}

    return StockMarketData(data)


def update_portfolio(stock_market_data: StockMarketData, portfolio: Portfolio, update: TradingAction):
    current_date = stock_market_data.companyName2DateValueArrayDict.get(update.sharesOfCompany.companyName)
    last_close = current_date[-1][1]

    print(f"Available cash: {portfolio.cash}")
    for share in portfolio.shares:
        if share.companyName is update.sharesOfCompany.companyName:
            amount = update.sharesOfCompany.amountOfShares
            trade_volume = amount * last_close

            if update.actionEnum is TradingActionEnum.BUY:
                print(f"Buying {amount} shares of {share.companyName} with volume of {trade_volume}")

                if trade_volume <= portfolio.cash:
                    share.amountOfShares += amount
                    portfolio.cash -= trade_volume
                else:
                    print(f"No sufficient cash reserve ({portfolio.cash}) for planned transaction with "
                          f"volume of {trade_volume}")
            elif update.actionEnum is TradingActionEnum.SELL:
                print(f"Selling {amount} shares of {share.companyName} with volume of {trade_volume}")

                share.amountOfShares -= amount
                portfolio.cash += trade_volume

    print(f"Resulting available cash after trade: {portfolio.cash}")
