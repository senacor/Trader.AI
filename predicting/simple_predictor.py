'''
Created on 08.11.2017

@author: jtymoszuk
'''
import abc
from predicting.predictor_interface import IPredictor


class SimplePredictor(IPredictor):
    '''
    Simple Predicator always returning last value form given input vector.
    '''

    def __init__(self):
        '''
        Constructor
        '''
        
    def doPredict(self, data:list) -> float:
        """ Always returns last value form given input vector.
    
        Args:
          data : historical stock values of a company 
        Returns:
          last value from input
        """
        return data[-1][-1] # return last value from input
        
