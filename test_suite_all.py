import unittest

from evaluating.evaluator_test import EvaluatorTest
from predicting.test.predictor_test import PredictingTest
from trading.test.trader_test import TraderTest

if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(EvaluatorTest)
    suite = unittest.TestLoader().loadTestsFromTestCase(PredictingTest)
    suite = unittest.TestLoader().loadTestsFromTestCase(TraderTest)

    unittest.TextTestRunner(verbosity=2).run(suite)
