import unittest

from predicting.test.simple_predictor_test import SimplePredictorTest
from predicting.test.perfect_predictor_test import PerfectPredictorTest
from predicting.test.nn_predictor_test import NnPredictorTest
from trading.test.buy_and_hold_trader_test import BuyAndHoldTraderTest
from trading.test.simple_trader_test import SimpleTraderTest
from trading.test.dql_trader_test import DqlTraderTest
from evaluating.test.evaluator_test import EvaluatorTest
from model.test.test_stockMarketData import TestStockMarketData

if __name__ == "__main__":

    test_classes = [SimplePredictorTest, PerfectPredictorTest, NnPredictorTest,
                    BuyAndHoldTraderTest, SimpleTraderTest, DqlTraderTest,
                    EvaluatorTest,
                    TestStockMarketData]

    suites = []
    for test in test_classes:
        suites.append(unittest.TestLoader().loadTestsFromTestCase(test))

    unittest.TextTestRunner(verbosity=2).run(unittest.TestSuite(suites))
