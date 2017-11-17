import datetime
from typing import List, Tuple

StockDataTuple = Tuple[datetime.date, float]
StockDataList = List[StockDataTuple]


class StockData:
    """
    Objects of this class comprise a list of tuples which in turn consist of a mapping between dates (type
    `datetime.date`) and stock prices (type `float`)
    """

    def __init__(self, stock_data: StockDataList):
        """
        Constructor
        Args:
            stock_data: A list of tuples with dates and the corresponding stock price.
             Structure: list[(datetime.date, float)]
        """
        self.__stock_data = stock_data

    def append(self, stock_data_item: StockDataTuple):
        """

        Args:
            stock_data_item:
        """
        self.__stock_data.append(stock_data_item)

    def iter(self):
        """
        Returns an iterator over the underlying list of tuples

        Returns:
            The iterator
        """
        return iter(self.__stock_data)

    def get(self, index: int):
        """
        Returns the `index`th item in the list of stock data
        Args:
            index: The index to get

        Returns:
            A tuple consisting of a date and the corresponding stock price
        """
        return self.__stock_data[index]

    def get_first(self):
        """
        Returns the first item in the list of stock data

        Returns:
            A tuple consisting of a date and the corresponding stock price
        """
        return self.__stock_data[0]

    def get_last(self):
        """
        Returns the last item in the list of stock data

        Returns:
            A tuple consisting of a date and the corresponding stock price
        """
        return self.__stock_data[-1]

    def get_from_offset(self, offset: int):
        """
        Calls `[offset:]` on the list of underlying stock data
        Args:
            offset: The offset to take

        Returns:
            A sub-list
        """
        return self.__stock_data[offset:]

    def get_row_count(self):
        """
        Determines how many data rows are available in the underlying stock market data

        Returns:
            The row count
        """
        return len(self.__stock_data)

    def index(self, item: StockDataTuple):
        """
        Calls `#index` on the underlying list of tuples
        Args:
            item: The item to look up the index for

        Returns:
            The index of the given `item`
        """
        return self.__stock_data.index(item)

    def copy_to_offset(self, offset: int):
        """
        Creates a copy of the underlying stock data and returns only the first `offset` items
        Args:
            offset: The offset to use

        Returns:
            A `StockData` object with only the first `offset` data rows
        """
        return StockData(self.__stock_data.copy()[:offset])
