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
from predicting.predictor.perfect_predictor import PerfectPredictor


class PerfectPredictorTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testConstructor(self):
        predictorA = PerfectPredictor(CompanyEnum.COMPANY_A)
        self.assertIsNotNone(predictorA)
        self.assertEqual(predictorA.company, CompanyEnum.COMPANY_A)
        self.assertEqual(predictorA.stock_values[0], 0.05962)
        self.assertEqual(predictorA.stock_values[-1], 101.610001)
        predictorB = PerfectPredictor(CompanyEnum.COMPANY_B)
        self.assertIsNotNone(predictorB)
        self.assertEqual(predictorB.company, CompanyEnum.COMPANY_B)
        self.assertEqual(predictorB.stock_values[0], 2.192523)
        self.assertEqual(predictorB.stock_values[-1], 151.350006)
       
    def testDoPredict(self):
        predictorA = PerfectPredictor(CompanyEnum.COMPANY_A)
        # only one possible value: take 03.01.2012 and predict 04.01.2012
        current_value = [dt.date(2012, 1, 3), 35.554108]
        future_value = 36.055264
        self.assertEqual(predictorA.doPredict([current_value]), future_value)
        # more than one possible values
        # TODO
    
if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(PerfectPredictorTest)
    unittest.TextTestRunner(verbosity=2).run(suite)
