'''
Created on 16.11.2017

Module for testing of PerfectPredictor

@author: rmueller
'''
import unittest

from datetime import date
import datetime as dt

import predicting
from model.CompanyEnum import CompanyEnum
from model.StockMarketData import StockMarketData
from predicting.predictor.perfect_predictor import PerfectPredictor


class PerfectPredictorTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testConstructor(self):
        # Create a perfect predictor for stock A
        predictorA = PerfectPredictor(CompanyEnum.COMPANY_A)
        self.assertIsNotNone(predictorA)
        self.assertIsNotNone(predictorA.stock_values)
        self.assertEqual(predictorA.stock_values[0][1], 0.05962)
        self.assertEqual(predictorA.stock_values[-1][1], 101.610001)

        # Create a perfect predictor for stock B
        predictorB = PerfectPredictor(CompanyEnum.COMPANY_B)
        self.assertIsNotNone(predictorB)
        self.assertIsNotNone(predictorB.stock_values)
        self.assertEqual(predictorB.stock_values[0][1], 2.192523)
        self.assertEqual(predictorB.stock_values[-1][1], 151.350006)

       
    def testDoPredict(self):
        predictorA = PerfectPredictor(CompanyEnum.COMPANY_A)

        # only one possible value: take 03.01.2012 and predict 04.01.2012
        current_value = [(dt.date(2012, 1, 3), 35.554108)]
        future_value = 36.055264
        self.assertEqual(predictorA.doPredict(current_value), future_value)

        # more than one possible values: take 08.01.1962 and predict 09.01.1962
        # because values from 03.01.1962 till 08.01.1962 are identical
        current_value = [dt.date(1962, 1, 8), 0.060421]
        future_value = 0.061621
        self.assertEqual(predictorA.doPredict([current_value]), future_value)
    
if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(PerfectPredictorTest)
    unittest.TextTestRunner(verbosity=2).run(suite)
