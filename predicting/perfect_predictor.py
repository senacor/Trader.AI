'''
Created on 08.11.2017

@author: rmueller
'''
import random

from model.CompanyEnum import CompanyEnum
from model.StockMarketData import StockMarketData
from predicting.predictor_interface import IPredictor
import numpy as np

import os
from definitions import DATASETS_DIR
from utils import load_keras_sequential, save_keras_sequential

MODEL_FILE_NAME = 'perfect_stock_a_predictor'

from evaluating.evaluator_utils import read_stock_market_data

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
        self.stock_values = []
        # TODO there is probably a more elegant way to load this data
        if company == CompanyEnum.COMPANY_A:
            file = open(os.path.join(DATASETS_DIR, 'stock_a_1962-2011.csv'), 'r')
            next(file)
            for line in file:
                self.stock_values.append(float(line.split(',')[5]))
            file.close()
            file = open(os.path.join(DATASETS_DIR, 'stock_a_2012-2017.csv'), 'r')
            next(file)
            for line in file:
                self.stock_values.append(float(line.split(',')[5]))
            file.close()
        elif company == CompanyEnum.COMPANY_B:
            file = open(os.path.join(DATASETS_DIR, 'stock_b_1962-2011.csv'), 'r')
            next(file)
            for line in file:
                self.stock_values.append(float(line.split(',')[5]))
            file.close()
            file = open(os.path.join(DATASETS_DIR, 'stock_b_2012-2017.csv'), 'r')
            next(file)
            for line in file:
                self.stock_values.append(float(line.split(',')[5]))
            file.close()
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
        assert isinstance(data[0], float)

        # find all indices containing the current value
        current_value = data[-1]
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
            assert False
