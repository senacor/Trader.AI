'''
Created on 09.11.2017

@author: jtymoszuk
'''
import dependency_injector.containers as containers
import dependency_injector.providers as providers

from trading.trader.simple_trader import SimpleTrader
from trading.trader.rnn_trader import RnnTrader
from predicting.predictor.random_predictor import RandomPredictor
from predicting.predictor.perfect_predictor import PerfectPredictor
from model.CompanyEnum import CompanyEnum
from trading.trader.buy_and_hold_trader import BuyAndHoldTrader
from predicting.predictor.nn_predictor import StockBNnPredictor,\
    StockANnPredictor



class Predictors(containers.DeclarativeContainer):
    """IoC container of predictor providers."""
 
    RandomPredictor = providers.Factory(RandomPredictor)
    
    PerfectPredictor_stock_a = providers.Factory(PerfectPredictor, CompanyEnum.COMPANY_A)    
    PerfectPredictor_stock_b = providers.Factory(PerfectPredictor, CompanyEnum.COMPANY_B)
    
    StockANnPredictor = providers.Factory(StockANnPredictor)
    StockBNnPredictor = providers.Factory(StockBNnPredictor)

 
class Traders(containers.DeclarativeContainer):
    """IoC container of trader providers."""
    
    """Simple Trader"""
    SimpleTrader_with_perfect_prediction = providers.Factory(
        SimpleTrader, 
        stock_a_predictor=Predictors.PerfectPredictor_stock_a, 
        stock_b_predictor=Predictors.PerfectPredictor_stock_b
        )
    
    SimpleTrader_with_random_prediction = providers.Factory(
        SimpleTrader, 
        stock_a_predictor=Predictors.RandomPredictor, 
        stock_b_predictor=Predictors.RandomPredictor
        )
    
    SimpleTrader_with_nn_prediction = providers.Factory(
        SimpleTrader, 
        stock_a_predictor=Predictors.StockANnPredictor, 
        stock_b_predictor=Predictors.StockBNnPredictor
        )

    """Buy and Hold Trader"""
    BuyAndHoldTrader = providers.Factory(
        BuyAndHoldTrader
        )
   
    """RNN Trader"""
    RnnTraderr_with_perfect_prediction = providers.Factory(
        RnnTrader, 
        stock_a_predictor=Predictors.PerfectPredictor_stock_a, 
        stock_b_predictor=Predictors.PerfectPredictor_stock_b
        )
    
    RnnTrader_with_random_prediction = providers.Factory(
        RnnTrader, 
        stock_a_predictor=Predictors.RandomPredictor, 
        stock_b_predictor=Predictors.RandomPredictor
        )
    
    RnnTrader_with_nn_prediction = providers.Factory(
        RnnTrader, 
        stock_a_predictor=Predictors.StockANnPredictor, 
        stock_b_predictor=Predictors.StockBNnPredictor
        )
