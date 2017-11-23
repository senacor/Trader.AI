from typing import Dict

from model.CompanyEnum import CompanyEnum
from model.StockData import StockData

StockMarketDataDict = Dict[CompanyEnum, StockData]


class StockMarketData:
    """
    Represents current and historical stick market data of all companies
    """

    def __init__(self, market_data: StockMarketDataDict):
        """
        Constructor

        Args:
            market_data: Dictionary containing current and historical data for all companies in the stock market.
             Structure: `Dict[CompanyEnum, StockData]`
        """
        self.__market_data = market_data

    def get_most_recent_trade_day(self):
        """
        Determines the latest trade day of this stock market data

        Returns:
            A `datetime.date` object with the latest trade day
        """
        return next(iter(self.__market_data.values())).get_last()[0]

    def get_most_recent_price(self, company_enum: CompanyEnum) -> float:
        """
        Determines the latest stock price of the given `company_enum`.
        Returns None if no stock price for the given company was found.

        Args:
            company_enum: The company to determine the stock price of

        Returns:
            The latest `company_enum`'s stock price or None.
        """
        company_data = self.__market_data.get(company_enum)
        if company_data is not None:
            return company_data.get_last()[1]
        else:
            return None

    def get_row_count(self) -> int:
        """
        Determines how many data rows are available for the first company in the underlying stock market data

        Returns:
            The row count
        """
        return next(iter(self.__market_data.values())).get_row_count()

    def __getitem__(self, company_enum: CompanyEnum) -> StockData:
        """
        Delivers data for the given `company_enum`, or `None` if no data can be found

        Args:
            company_enum: The company to return the data for

        Returns:
            A list of `StockData` for the given company
        """
        return self.__market_data.get(company_enum)

    def get_number_of_companies(self) -> int:
        """
        Returns number of companies stored in this market data.

        Returns:
            Number of companies as integer.
        """
        return len(self.__market_data)

    def get_companies(self):
        """
        Returns a list of companies stored in this market data

        Returns:
            The list of companies
        """
        return list(self.__market_data.keys())

    def check_data_length(self) -> bool:
        """
        Checks if all underlying stock data lists have the same count. Does this by extracting every
        row count, inserting those numbers into a set and checking if this set has the length of 1

        Returns:
            `True` if all value rows have the same length, `False` if not
        """
        return len(set([stock_data.get_row_count() for stock_data in self.__market_data.values()])) == 1
