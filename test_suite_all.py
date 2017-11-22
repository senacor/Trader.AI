import unittest

from model.test.portfolio_test import TestPortfolio
from model.test.stock_data_test import TestStockData
from trading.test.buy_and_hold_trader_test import BuyAndHoldTraderTest
from trading.test.simple_trader_test import SimpleTraderTest
from trading.test.dql_trader_test import DqlTraderTest
from evaluating.test.portfolio_evaluator_test import EvaluatorTest, UtilsTest
from model.test.stock_market_data_test import TestStockMarketData
from predicting.test.reference.random_predictor_test import RandomPredictorTest
from predicting.test.reference.perfect_predictor_test import PerfectPredictorTest
from predicting.test.reference.nn_value_predictor_test import NnValuePredictorTest

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
