'''
Created on 08.11.2017

Module for testing of all predicting components

@author: jtymoszuk
'''
import unittest

from datetime import date
from depenedency_injection_containers import Predictors


class SimplePredictorTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass
       
    def testSimplePredictor(self):

        sp = Predictors.RandomPredictor() 
        
        inputData = list()
        
        today = date(2017, 11, 8)
        yesterday = date(2017, 11, 8)
        
        tuple1 = (yesterday, 2.0)
        tuple2 = (today, 3.0)
        
        inputData.append(tuple1)
        inputData.append(tuple2)

        result = sp.doPredict(inputData)
        
        self.assertNotEqual(result, 3.0)

    
if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(SimplePredictorTest)
    unittest.TextTestRunner(verbosity=2).run(suite)
