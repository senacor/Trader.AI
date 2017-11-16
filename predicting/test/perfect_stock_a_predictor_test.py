'''
Created on 09.11.2017

Module for testing of all predicting components

@author: rmueller
'''
import unittest

import evaluating.evaluator_utils
from depenedency_injection_containers import Predictors
from definitions import DATASETS_DIR
from predicting.predictor.nn_predictor import StockANnPredictor
from trading.model.trader_interface import CompanyEnum
from utils import read_stock_market_data

class PerfectStockAPredictorTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass
       
    def testPerfectStockAPredictor(self):
        # Load predictor
        predictor = StockANnPredictor()


        # Get stock data from Apple stock
        input = read_stock_market_data([[CompanyEnum.COMPANY_A, 'AAPL']], path=DATASETS_DIR).market_data[CompanyEnum.COMPANY_A]
        self.assertTrue( len(input) >= 0)

        # Get a prediction
        predictedValue = predictor.doPredict(data=input)

        self.assertGreaterEqual(predictedValue, 0.0)

    
if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(PerfectStockAPredictorTest)
    unittest.TextTestRunner(verbosity=2).run(suite)
