'''
Created on 08.11.2017

@author: jtymoszuk
'''
import abc

class IPredictor(metaclass=abc.ABCMeta):
    '''
    Predictor interface
    '''

    @abc.abstractmethod
    def doPredict(self, data:list) -> float:
        """ Predicts future stock value of company using it's given historical values 
    
        Args:
          data : historical stock values of a company 
        Returns:
          next predicted value of the company
        """
        pass