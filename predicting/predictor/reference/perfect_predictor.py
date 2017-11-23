'''
Created on 16.11.2017

@author: rmueller
'''
from definitions import PERIOD_1, PERIOD_2, PERIOD_3
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
        # TODO Our whole algorithm relies on correct values in CompanyEnum. So this assertion is needless IMO (jh)
        assert company.value == 'stock_a' or company.value == 'stock_b'

        # Load all stock data, but only save it for the given company
        # TODO Why do we read all/both company's data? We only need one, see line underneath (jh)
        stock_market_data = read_stock_market_data([CompanyEnum.COMPANY_A, CompanyEnum.COMPANY_B],
                                                   [PERIOD_1, PERIOD_2, PERIOD_3])
        self.stock_data = stock_market_data[company]

    # TODO Why providing `StockData` as method parameter when it has been already constructed/read in constructor? (jh)
    def doPredict(self, data: StockData) -> float:
        """ Use the loaded stock values to predict the next stock value.
    
        Args:
          data : historical stock values of
        Returns:
          predicted next stock value for that company
        """
        assert data is not None and data.get_row_count() > 0

        # TODO Don't do this here. As already stated above: Our whole algorithm relies on these assumptions. Either we
        # should assert this at central places or not at all (jh - I prefer 'not at all')
        assert len(data.get_first()) == 2
        assert isinstance(data.get_first()[0], dt.date)
        assert isinstance(data.get_first()[1], float)

        (current_date, current_value) = data.get_last()
        index = self.stock_data.index((current_date, current_value))
        if index is not None and index < self.stock_data.get_row_count() - 1:
            (_, next_value) = self.stock_data.get(index + 1)
            return next_value
        else:
            logger.error(f"Couldn't make a perfect prediction for the day after {current_date}")
            assert False
