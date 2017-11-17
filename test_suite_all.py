import unittest

from predicting.test.predictor_test import PredictingTest
from predicting.test.perfect_predictor_test import PerfectPredictorTest
from predicting.test.nn_predictor_test import NnPredictorTest
from trading.test.trader_test import TraderTest
from evaluating.test.evaluator_test import EvaluatorTest

if __name__ == "__main__":

    test_classes = [PredictingTest, PerfectPredictorTest, NnPredictorTest, TraderTest, EvaluatorTest]

    suites = []
    for test in test_classes:
        suites.append(unittest.TestLoader().loadTestsFromTestCase(test))

    unittest.TextTestRunner(verbosity=2).run(unittest.TestSuite(suites))
