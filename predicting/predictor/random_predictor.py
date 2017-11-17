'''
Created on 08.11.2017

@author: jtymoszuk
'''
import random
from model.IPredictor import IPredictor


class RandomPredictor(IPredictor):
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
          last value from input +/- Random value between -1 and +1
        """
        return data[-1][-1] + random.uniform(-1.0, 1.0)  # return last value from input +- random value between -1 and +1
        
