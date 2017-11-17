'''
Created on 16.11.2017

@author: rmueller
'''
from model.IPredictor import IPredictor
from model.CompanyEnum import CompanyEnum
import datetime as dt

from model.StockData import StockData
from utils import read_stock_market_data
from logger import logger

class PerfectPredictor(IPredictor):
    '''
    This predictor perfectly predicts the next stock price because it cheats.
    '''

    def __init__(self, company: CompanyEnum):
        """
        Constructor:
            Load all available stock data for the given company.

        Args:
            company: The company whose stock values we should predict.
        """
        # This predictor is for stock A or stock B only!
        assert company.value == 'stock_a' or company.value == 'stock_b'

        # Load all stock data, but only save it for the given company
        stock_market_data = read_stock_market_data([CompanyEnum.COMPANY_A, CompanyEnum.COMPANY_B],
                                                   ['1962-2011', '2012-2017'])
        self.stock_values = stock_market_data.get_for_company(company)

    def doPredict(self, data: StockData) -> float:
        """ Use the loaded stock values to predict the next stock value.
    
        Args:
          data : historical stock values of
        Returns:
          predicted next stock value for that company
        """
        assert data is not None and data.get_row_count() > 0
        assert len(data.get_first()) == 2
        assert isinstance(data.get_first()[0], dt.date)
        assert isinstance(data.get_first()[1], float)

        (current_date, current_value) = data.get_last()
        index = self.stock_values.index((current_date, current_value))
        if index is not None and index < self.stock_values.get_row_count() - 1:
            (_, next_value) = self.stock_values.get(index + 1)
            return next_value
        else:
            logger.error(f"Couldn't make a perfect prediction for the day after {current_date}")
            assert False
