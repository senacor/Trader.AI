'''
Created on 09.11.2017

@author: jtymoszuk
'''
import dependency_injector.containers as containers
import dependency_injector.providers as providers

from trading.trader.simple_trader import SimpleTrader
from trading.trader.dql_trader import DqlTrader
from model.CompanyEnum import CompanyEnum
from trading.trader.buy_and_hold_trader import BuyAndHoldTrader
from predicting.predictor.reference.random_predictor import RandomPredictor
from predicting.predictor.reference.perfect_predictor import PerfectPredictor
from predicting.predictor.reference.nn_binary_predictor import StockANnBinaryPredictor,\
    StockBNnBinaryPredictor
from predicting.predictor.reference.nn_perfect_binary_predictor import StockANnPerfectBinaryPredictor,\
    StockBNnPerfectBinaryPredictor



class Predictors(containers.DeclarativeContainer):
    """IoC container of predictor providers."""
 
    """ Random predictor delivering value of last share +- Random[0,1]"""
    RandomPredictor = providers.Factory(RandomPredictor)
    
    """ Perfect predictors knowing future"""
    PerfectPredictor_stock_a = providers.Factory(PerfectPredictor, CompanyEnum.COMPANY_A)    
    PerfectPredictor_stock_b = providers.Factory(PerfectPredictor, CompanyEnum.COMPANY_B)
    
    """ Predictors based on neural networks, trying to estimate next future value of share"""
    #Currently not in use
    #StockANnValuePredictor = providers.Factory(StockANnValuePredictor)
    #StockBNnValuePredictor = providers.Factory(StockBNnValuePredictor)
    
    """ Binary predictors based on neural networks trained only with historical data (till 2011). 
    Predictors are estimating only if next value will go up or down - returned result is then value of last share +- constant value """
    StockANnBinaryPredictor = providers.Factory(StockANnBinaryPredictor)
    StockBNnBinaryPredictor = providers.Factory(StockBNnBinaryPredictor)
    
    """ Predictors based on neural networks trained only with all available data (till 2017).
    Predictors are estimating only if next value will go up or down - returned result is then value of last share +- constant value """
    StockANnPerfectBinaryPredictor = providers.Factory(StockANnPerfectBinaryPredictor)
    StockBNnPerfectBinaryPredictor = providers.Factory(StockBNnPerfectBinaryPredictor)

 
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
    
    SimpleTrader_with_nn_binary_perfect_prediction = providers.Factory(
        SimpleTrader,
        stock_a_predictor=Predictors.StockANnPerfectBinaryPredictor,
        stock_b_predictor=Predictors.StockBNnPerfectBinaryPredictor
        )
    
    SimpleTrader_with_nn_binary_prediction = providers.Factory(
        SimpleTrader,
        stock_a_predictor=Predictors.StockANnBinaryPredictor,
        stock_b_predictor=Predictors.StockBNnBinaryPredictor
        )

    """Buy and Hold Trader"""
    BuyAndHoldTrader = providers.Factory(
        BuyAndHoldTrader
        )
   
    """DQL Trader"""
    DqlTrader_with_perfect_prediction = providers.Factory(
        DqlTrader,
        stock_a_predictor=Predictors.PerfectPredictor_stock_a,
        stock_b_predictor=Predictors.PerfectPredictor_stock_b
        )
    
    DqlTrader_with_random_prediction = providers.Factory(
        DqlTrader,
        stock_a_predictor=Predictors.RandomPredictor,
        stock_b_predictor=Predictors.RandomPredictor
        )
    
    DqlTrader_with_nn_binary_perfect_prediction = providers.Factory(
        DqlTrader,
        stock_a_predictor=Predictors.StockANnPerfectBinaryPredictor,
        stock_b_predictor=Predictors.StockBNnPerfectBinaryPredictor
        )
    
    DqlTrader_with_nn_binary_prediction = providers.Factory(
        DqlTrader,
        stock_a_predictor=Predictors.StockANnBinaryPredictor,
        stock_b_predictor=Predictors.StockBNnBinaryPredictor
        )
