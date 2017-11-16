'''
Created on 09.11.2017

@author: jtymoszuk
'''
import dependency_injector.containers as containers
import dependency_injector.providers as providers

from trading.trader.simple_trader import SimpleTrader
from trading.trader.random_trader import RandomTrader
from trading.trader.rnn_trader import RnnTrader
from predicting.simple_predictor import SimplePredictor
from predicting.perfect_stock_a_predictor import PerfectStockAPredictor


class Predictors(containers.DeclarativeContainer):
    """IoC container of predictor providers."""
 
    simple_predictor = providers.Factory(SimplePredictor)
    perfect_stock_a_predictor = providers.Factory(PerfectStockAPredictor)

 
class Traders(containers.DeclarativeContainer):
    """IoC container of trader providers."""
    
    simple_trader_for_test = providers.Factory(SimpleTrader, stock_a_predictor=Predictors.perfect_stock_a_predictor, stock_b_predictor=None)
    simple_trader_with_perfect_stock_aprediction = providers.Factory(SimpleTrader, stock_a_predictor=Predictors.perfect_stock_a_predictor, stock_b_predictor=Predictors.simple_predictor)
    simple_trader_with_simple_predictors = providers.Factory(SimpleTrader, stock_a_predictor=Predictors.simple_predictor, stock_b_predictor=Predictors.simple_predictor)

    rnn_trader_with_simple_predictors = providers.Factory(RnnTrader, stock_a_predictor=Predictors.simple_predictor, stock_b_predictor=Predictors.simple_predictor)
    
    random_trader = providers.Factory(RandomTrader)

    

