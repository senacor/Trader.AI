"""
Created on 23.11.2017

Module for testing of predicting components

@author: jtymoszuk
"""
import unittest
from predicting.predictor.team_green.team_green_predictor import TeamGreenStockAPredictor
from model.CompanyEnum import CompanyEnum
from definitions import PERIOD_1
from utils import read_stock_market_data


class TeamGreenPredictorTest(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testStockANnPredictor(self):
        # Get stock A data
        stock_market_data = read_stock_market_data([CompanyEnum.COMPANY_A], [PERIOD_1])
        stock_data = stock_market_data[CompanyEnum.COMPANY_A]

        # Load stock A predictor
        predictor = TeamGreenStockAPredictor()

        # Check prediction
        stock_prediction = predictor.doPredict(stock_data)
        self.assertEqual(stock_prediction, 0.0)


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TeamGreenPredictorTest)
    unittest.TextTestRunner(verbosity=2).run(suite)
