'''
Created on 16.11.2017

@author: rmueller
'''
from model.CompanyEnum import CompanyEnum
from predicting.model.IPredictor import IPredictor
import datetime as dt
from utils import read_stock_market_data_conveniently

from utils import read_stock_market_data

import os
from definitions import DATASETS_DIR
from utils import load_keras_sequential, save_keras_sequential

MODEL_FILE_NAME_STOCK_A = 'perfect_stock_a_predictor'

from utils import read_stock_market_data

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
        if company == CompanyEnum.COMPANY_A:
            stock_market_data = read_stock_market_data_conveniently([CompanyEnum.COMPANY_A], ['1962-2011', '2012-2017'])
            self.stock_values = stock_market_data.get_stock_data_for_company(company)
        elif company == CompanyEnum.COMPANY_B:
            stock_market_data = read_stock_market_data_conveniently([CompanyEnum.COMPANY_B], ['1962-2011', '2012-2017'])
            self.stock_values = stock_market_data.get_stock_data_for_company(company)
        else:
            print(f"perfect_stock_predictor: Cannot handle company {company}")
            assert False

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
