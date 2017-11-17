import unittest

from model.test.test_stockMarketData import TestStockMarketData
from predicting.test.simple_predictor_test import SimplePredictorTest
from predicting.test.perfect_predictor_test import PerfectPredictorTest
from predicting.test.nn_predictor_test import NnPredictorTest
from trading.test.trader_test import TraderTest
from evaluating.test.evaluator_test import EvaluatorTest

if __name__ == "__main__":

    test_classes = [SimplePredictorTest, PerfectPredictorTest, NnPredictorTest, TraderTest, EvaluatorTest,
                    TestStockMarketData]

    suites = []
    for test in test_classes:
        suites.append(unittest.TestLoader().loadTestsFromTestCase(test))

    unittest.TextTestRunner(verbosity=2).run(unittest.TestSuite(suites))
