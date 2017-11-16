from model.CompanyEnum import CompanyEnum


class StockMarketData:
    """
    Represents current and historical stick market data of all companies
    """

    def __init__(self, market_data: dict):
        """
        Constructor
        :param market_data: Dictionary containing current and historical data for all companies in Stock Market.
        Structure: key: company name as string, value: 2 column array: datetime.date, float
        """
        self.market_data = market_data

    def get_most_recent_trade_day(self):
        return next(iter(self.market_data.values()))[-1][0]

    def get_most_recent_price(self, stock: str):
        return self.market_data.get(stock)[-1][1]

    def get_row_count(self):
        return len(next(iter(self.market_data.values())))

    def get_stock_data_for_company(self, company_enum: CompanyEnum):
        """
        Delivers data for given CompanyEnum, or None if nothing found
        """
        return self.market_data.get(company_enum.value)
