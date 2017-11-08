'''
Created on 08.11.2017

Module for testing of all trader components

@author: jtymoszuk
'''
import unittest

from predicting.simple_predictor import SimplePredictor


class RandomTraderTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass
       
    def testSimplePredictor(self):
        sp = SimplePredictor()     
        
        inputData = [1.0, 2.0, 3.0]

        result = sp.doPredict(inputData)
        
        self.assertEqual(result, 3.0)

    
if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(RandomTraderTest)
    unittest.TextTestRunner(verbosity=2).run(suite)
