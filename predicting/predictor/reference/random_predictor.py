"""
Created on 08.11.2017

@author: jtymoszuk
"""
import random
from model.IPredictor import IPredictor
from model.StockData import StockData


class RandomPredictor(IPredictor):
    """
    Simple Predictor always returning last value form given input vector.
    """

    def __init__(self):
        """
        Constructor
        """

    def doPredict(self, data: StockData) -> float:
        """ Always returns last value form given input vector.
    
        Args:
          data : historical stock values of a company 
        Returns:
          last value from input +/- Random value between -1 and +1
        """

        # return last value from input +- random value between -1 and +1
        return data.get_last()[-1] + random.uniform(-1.0, 1.0)
