'''
Created on 09.11.2017

Module for testing of all predicting components

@author: rmueller
'''
import unittest

import evaluating.evaluator
from depenedency_injection_containers import Predictors
from definitions import DATASETS_DIR
from trading.trader_interface import CompanyEnum

class PerfectStockAPredictorTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass
       
    def testPerfectStockAPredictor(self):
        # Load predictor
        predictor = Predictors.perfectStockAPredictor()


        # Get stock data from Apple stock
        input = evaluating.evaluator.read_stock_market_data([[CompanyEnum.COMPANY_A.value,'AAPL']], path=DATASETS_DIR).market_data[CompanyEnum.COMPANY_A.value]
        self.assertTrue( len(input) >= 0)

        # Get a prediction
        predictedValue = predictor.doPredict(data=input)

        self.assertGreaterEqual(predictedValue, 0.0)

    
if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(PerfectStockAPredictorTest)
    unittest.TextTestRunner(verbosity=2).run(suite)
