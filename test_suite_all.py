import unittest

from evaluating.test.evaluator_test import EvaluatorTest
from predicting.test.predictor_test import PredictingTest
from trading.test.trader_test import TraderTest
from predicting.test.perfect_stock_a_predictor_test import PerfectStockAPredictorTest

if __name__ == "__main__":

    test_classes = [EvaluatorTest, PredictingTest, PerfectStockAPredictorTest, TraderTest]

    suites = []
    for test in test_classes:
        suites.append(unittest.TestLoader().loadTestsFromTestCase(test))

    unittest.TextTestRunner(verbosity=2).run(unittest.TestSuite(suites))
