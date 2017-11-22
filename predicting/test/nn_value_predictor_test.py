'''
Created on 09.11.2017

Module for testing of all predicting components

@author: rmueller
'''
import unittest
from predicting.predictor.nn_value_predictor import StockANnValuePredictor, StockBNnValuePredictor
from model.CompanyEnum import CompanyEnum
from utils import read_stock_market_data

class NnValuePredictorTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass
       
    def testStockANnPredictor(self):
        # Get stock A data
        stock_market_data = read_stock_market_data([CompanyEnum.COMPANY_A], ['1962-2011'])
        stock_data = stock_market_data.get_for_company(CompanyEnum.COMPANY_A)

        # Load stock A predictor
        predictor = StockANnValuePredictor()

        # Check that prediction is within 10% of the most recent stock value
        stock_value = stock_market_data.get_most_recent_price(CompanyEnum.COMPANY_A)
        stock_prediction = predictor.doPredict(stock_data)
        if predictor.trained:
            self.assertGreaterEqual(stock_prediction, stock_value * 0.9)
            self.assertLessEqual(stock_prediction, stock_value * 1.1)

    def testStockBNnPredictor(self):
        # Get stock B data
        stock_market_data = read_stock_market_data([CompanyEnum.COMPANY_B], ['1962-2011'])
        stock_data = stock_market_data.get_for_company(CompanyEnum.COMPANY_B)

        # Load stock B predictor
        predictor = StockBNnValuePredictor()

        # Check that prediction for a trained model is within 10% of the most recent stock value
        stock_value = stock_market_data.get_most_recent_price(CompanyEnum.COMPANY_B)
        stock_prediction = predictor.doPredict(stock_data)
        if predictor.trained:
            self.assertGreaterEqual(stock_prediction, stock_value * 0.9)
            self.assertLessEqual(stock_prediction, stock_value * 1.1)
    
if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(NnValuePredictorTest)
    unittest.TextTestRunner(verbosity=2).run(suite)