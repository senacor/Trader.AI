"""
Created on 08.11.2017

Module for testing of all predicting components

@author: jtymoszuk
"""
import unittest

from datetime import date
from dependency_injection_containers import Predictors
from model.StockData import StockData


class RandomPredictorTest(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testRandomPredictor(self):
        sp = Predictors.RandomPredictor()

        input_data = StockData([])

        today = date(2017, 11, 8)
        yesterday = date(2017, 11, 8)

        tuple1 = (yesterday, 2.0)
        tuple2 = (today, 3.0)

        input_data.append(tuple1)
        input_data.append(tuple2)

        result = sp.doPredict(input_data)

        self.assertNotEqual(result, 3.0)


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(RandomPredictorTest)
    unittest.TextTestRunner(verbosity=2).run(suite)
