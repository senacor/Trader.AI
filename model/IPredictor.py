"""
Created on 08.11.2017

@author: jtymoszuk
"""
import abc

from model.StockData import StockData


class IPredictor(metaclass=abc.ABCMeta):
    """
    Predictor interface
    """

    @abc.abstractmethod
    def doPredict(self, data: StockData) -> float:
        """
        Predicts future stock value of company using its given historical values
    
        Args:
          data: Historical stock values of a company

        Returns:
          The next predicted stock value of the company
        """
        pass
