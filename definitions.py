'''
Created on 09.11.2017

@author: jtymoszuk
'''
import os

# This is Project Root
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

DATASETS_DIR = os.path.join(ROOT_DIR, 'datasets')
JSON_DIR = os.path.join(ROOT_DIR, 'json')

# Fixed periods for training and test data
PERIOD_1 = "1962-2011"  # Training data
PERIOD_2 = "2012-2015"  # Test data (for teams)
PERIOD_3 = "2016-2017"  # Test data (for module evaluation)

# Names for DqlTraders trained with different predictors
DQLTRADER_PERFECT_PREDICTOR = 'dql_trader_perfect'
DQLTRADER_PERFECT_NN_BINARY_PREDICTOR = 'dql_trader_perfect_nn_binary'
DQLTRADER_NN_BINARY_PREDICTOR = 'dql_trader_nn_binary'
DQLTRADER_RANDOM_PREDICTOR = 'dql_trader_random'