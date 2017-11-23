from unittest import TestCase

from datetime import date

import numpy as np

from model.StockData import StockData


def get_test_data():
    return StockData([(date(2017, 1, 1), 150.0), (date(2017, 1, 2), 200.0)])


class TestStockData(TestCase):
    """
    This tests an old implementation of `get_dates` and `get_values` against an easier one
    """

    def test_get_dates(self):
        old_implementation = np.array([[x[0] for x in iter(get_test_data())]])[0].tolist()

        assert get_test_data().get_dates() == old_implementation

    def test_get_values(self):
        old_implementation = np.array([[x[1] for x in iter(get_test_data())]])[0].tolist()

        assert get_test_data().get_values() == old_implementation
