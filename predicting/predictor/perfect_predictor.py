'''
Created on 08.11.2017

@author: rmueller
'''
import random

from model.CompanyEnum import CompanyEnum
from model.StockMarketData import StockMarketData
from predicting.model.IPredictor import IPredictor
import numpy as np

import datetime as dt

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
            Load all available stock data

        Args:
            company: The company which stock values we should predict
        """
        self.company = company

        # TODO there is probably a more elegant way to load this data
        self.stock_values = []
        if company == CompanyEnum.COMPANY_A:
            old_values = read_stock_market_data([(company, 'stock_a_1962-2011')], DATASETS_DIR)
            new_values = read_stock_market_data([(company, 'stock_a_2012-2017')], DATASETS_DIR)
            for (_, value) in old_values.get_stock_data_for_company(company):
                self.stock_values.append(value)
            for (_, value) in new_values.get_stock_data_for_company(company):
                self.stock_values.append(value)
        elif company == CompanyEnum.COMPANY_B:
            old_values = read_stock_market_data([(company, 'stock_b_1962-2011')], DATASETS_DIR)
            new_values = read_stock_market_data([(company, 'stock_b_2012-2017')], DATASETS_DIR)
            for (_, value) in old_values.get_stock_data_for_company(company):
                self.stock_values.append(value)
            for (_, value) in new_values.get_stock_data_for_company(company):
                self.stock_values.append(value)
        else:
            print(f"perfect_stock_predictor: Cannot handle company {company}")
            assert False

    def doPredict(self, data:list) -> float:
        """ Use the loaded trained neural network to predict the next stock value.
    
        Args:
          data : historical stock values of
        Returns:
          predicted next stock value for that company
        """
        assert data is not None and len(data) > 0
        assert len(data[0]) == 2
        assert isinstance(data[0][0], dt.date)
        assert isinstance(data[0][1], float)

        # find all indices containing the current value
        current_value = data[-1][1]
        print(current_value)
        indices = [i for i, x in enumerate(self.stock_values) if x == current_value]
        print(indices)

        # if there is more than one index, take one randomly
        if len(indices) == 1:
            return self.stock_values[indices[0] + 1]
        elif len(indices) == 1:
            index = random.choice(indices) # TODO actually, we could do this without random by using pattern matching
            return self.stock_values[index + 1]
        else:
            print(f"perfect_stock_predictor: Could not find current stock value {current_value}")
            return 0.0
