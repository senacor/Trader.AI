import json
from pprint import pprint

from trading.random_trader import RandomTrader
from trading.trader_interface import Portfolio, SharesOfCompany, StockMarketData

rt = RandomTrader()


# tradingAction = rt.doTrade(portfolio, stockMarketData)

def read_portfolio() -> Portfolio:
    json_data = open("json/portfolio.json").read()
    data = json.loads(json_data)

    shares_list = list()
    for share in data['shares']:
        shares_list.append(SharesOfCompany(share['name'], share['amount']))

    pprint(shares_list[0].companyName)
    pprint(shares_list[0].amountOfShares)
    pprint(data['cash'])
    return Portfolio(data['cash'], shares_list)


def read_stock_market_data() -> StockMarketData:
    return StockMarketData()


read_portfolio()
read_stock_market_data()
