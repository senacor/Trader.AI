'''
Created on 09.11.2017

@author: jtymoszuk
'''
import dependency_injector.containers as containers
import dependency_injector.providers as providers

from trading.simple_trader import SimpleTrader
from trading.random_trader import RandomTrader
from predicting.simple_predictor import SimplePredictor
from predicting.perfect_stock_a_predictor import PerfectStockAPredictor


class Predictors(containers.DeclarativeContainer):
    """IoC container of predictor providers."""
 
    simplePredictor = providers.Factory(SimplePredictor)
    perfectStockAPredictor = providers.Factory(PerfectStockAPredictor)

 
class Traders(containers.DeclarativeContainer):
    """IoC container of trader providers."""
    
    simpleTraderForTest = providers.Factory(SimpleTrader, stockAPredictor=Predictors.perfectStockAPredictor, stockBPredictor=None)
    simpleTraderWithPerfectStockAPrediction = providers.Factory(SimpleTrader, stockAPredictor=Predictors.perfectStockAPredictor, stockBPredictor=Predictors.simplePredictor)
    simpleTraderWithSimplePredictors = providers.Factory(SimpleTrader, stockAPredictor=Predictors.simplePredictor, stockBPredictor=Predictors.simplePredictor)
    
    randomTrader = providers.Factory(RandomTrader)

    

