'''
Created on 16.11.2017

@author: rmueller
'''
from predicting.model.IPredictor import IPredictor
from model.CompanyEnum import CompanyEnum
import datetime as dt
from utils import read_stock_market_data_conveniently

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
        stock_market_data = read_stock_market_data_conveniently([CompanyEnum.COMPANY_A, CompanyEnum.COMPANY_B],
                                                                ['1962-2011', '2012-2017'])
        self.stock_values = stock_market_data.get_stock_data_for_company(company)

    def doPredict(self, data:list) -> float:
        """ Use the loaded stock values to predict the next stock value.
    
        Args:
          data : historical stock values of
        Returns:
          predicted next stock value for that company
        """
        assert data is not None and len(data) > 0
        assert len(data[0]) == 2
        assert isinstance(data[0][0], dt.date)
        assert isinstance(data[0][1], float)

        (current_date, current_value) = data[-1]
        index = self.stock_values.index((current_date, current_value))
        assert index is not None and index < len(self.stock_values) -1
        (_, next_value) = self.stock_values[index +1 ]
        return next_value
