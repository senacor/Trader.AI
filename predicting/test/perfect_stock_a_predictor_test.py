'''
Created on 09.11.2017

Module for testing of all predicting components

@author: rmueller
'''
import unittest

import evaluating.evaluator
from trading.trader_interface import StockMarketData

from predicting.perfect_stock_a_predictor import PerfectStockAPredictor
from datetime import date
import numpy as np


class PerfectStockAPredictorTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass
       
    def testPerfectStockAPredictor(self):
        # Load predictor
        predictor = PerfectStockAPredictor()

        # Get stock data from Apple stock
        input = evaluating.evaluator.read_stock_market_data(['AAPL'], path='../../datasets/').market_data['AAPL']
        self.assertTrue( len(input) >= 0)

        # Get a prediction
        predictedValue = predictor.doPredict(data=input)

        self.assertGreaterEqual(predictedValue, 0.0)

    
if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(PerfectStockAPredictorTest)
    unittest.TextTestRunner(verbosity=2).run(suite)
