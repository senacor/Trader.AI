"""
Created on 16.11.2017

Module for testing of PerfectPredictor

@author: rmueller
"""
import unittest

import datetime as dt

from model.CompanyEnum import CompanyEnum
from model.StockData import StockData
from predicting.predictor.reference.perfect_predictor import PerfectPredictor


class PerfectPredictorTest(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testConstructor(self):
        # Create a perfect predictor for stock A
        predictor_a = PerfectPredictor(CompanyEnum.COMPANY_A)
        self.assertIsNotNone(predictor_a)
        self.assertIsNotNone(predictor_a.stock_data)
        self.assertEqual(predictor_a.stock_data.get(0)[1], 0.05962)
        self.assertEqual(predictor_a.stock_data.get_last()[1], 101.610001)

        # Create a perfect predictor for stock B
        predictor_b = PerfectPredictor(CompanyEnum.COMPANY_B)
        self.assertIsNotNone(predictor_b)
        self.assertIsNotNone(predictor_b.stock_data)
        self.assertEqual(predictor_b.stock_data.get(0)[1], 2.192523)
        self.assertEqual(predictor_b.stock_data.get_last()[1], 151.350006)

    def testDoPredictStockA(self):
        predictor = PerfectPredictor(CompanyEnum.COMPANY_A)

        # only one possible value: take 30.12.2011 and predict 03.01.2012
        current_value = StockData([(dt.date(2011, 12, 30), 34.802376)])
        future_value = 35.554108
        self.assertEqual(predictor.doPredict(current_value), future_value)

        # only one possible value: take 03.01.2012 and predict 04.01.2012
        current_value = StockData([(dt.date(2012, 1, 3), 35.554108)])
        future_value = 36.055264
        self.assertEqual(predictor.doPredict(current_value), future_value)

        # more than one possible values: take 08.01.1962 and predict 09.01.1962
        # because values from 03.01.1962 till 08.01.1962 are identical
        current_value = StockData([(dt.date(1962, 1, 8), 0.060421)])
        future_value = 0.061621
        self.assertEqual(predictor.doPredict(current_value), future_value)

    def testDoPredictStockB(self):
        predictor = PerfectPredictor(CompanyEnum.COMPANY_B)

        # only one possible value: take 30.12.2011 and predict 03.01.2012
        current_value = StockData([(dt.date(2011, 12, 30), 157.077850)])
        future_value = 159.145142
        self.assertEqual(predictor.doPredict(current_value), future_value)

        # only one possible value: take 03.01.2012 and predict 04.01.2012
        current_value = StockData([(dt.date(2012, 1, 3), 159.145142)])
        future_value = 158.495911
        self.assertEqual(predictor.doPredict(current_value), future_value)
