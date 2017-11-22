import unittest

from predicting.test.random_predictor_test import RandomPredictorTest
from model.test.test_portfolio import TestPortfolio
from model.test.test_stockData import TestStockData
from predicting.test.perfect_predictor_test import PerfectPredictorTest
from predicting.test.nn_value_predictor_test import NnValuePredictorTest
from trading.test.buy_and_hold_trader_test import BuyAndHoldTraderTest
from trading.test.simple_trader_test import SimpleTraderTest
from trading.test.dql_trader_test import DqlTraderTest
from evaluating.test.evaluator_test import EvaluatorTest, UtilsTest
from model.test.test_stockMarketData import TestStockMarketData

if __name__ == "__main__":

    test_classes = [
        # Trader
        BuyAndHoldTraderTest,
        SimpleTraderTest,
        DqlTraderTest,

        # Predictor
        RandomPredictorTest,
        PerfectPredictorTest,
        NnValuePredictorTest,

        # Evaluator
        EvaluatorTest,

        # Model
        TestPortfolio,
        TestStockMarketData,
        TestStockData,

        # Misc
        UtilsTest
    ]

    suites = []
    for test in test_classes:
        suites.append(unittest.TestLoader().loadTestsFromTestCase(test))

    unittest.TextTestRunner(verbosity=2).run(unittest.TestSuite(suites))
