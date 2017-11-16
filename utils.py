'''
Created on 15.11.2017

Utility functions

@author: jtymoszuk
'''
import os
from keras.models import Sequential
from keras.models import model_from_json
from definitions import ROOT_DIR, DATASETS_DIR
from model.StockMarketData import StockMarketData
import numpy
from model.CompanyEnum import CompanyEnum
import datetime as dt


def save_keras_sequential(model: Sequential, relative_path: str, file_name_without_extension: str) -> bool:
    """
    Saves a Keras Sequential in File System
    
    Args:
        model : Sequential to save
        relative_path : relative path in project
        file_name_without_extension : file name without extension, will be used for json with models and h5 with weights.
    Returns:
        True if successful, False otherwise, never None
    """
    try:
        model_as_json = model.to_json()
        
        json_file = open(os.path.join(ROOT_DIR, relative_path, file_name_without_extension + '.json'), "w")
        json_file.write(model_as_json)
        json_file.close()
        
        model.save_weights(os.path.join(ROOT_DIR, relative_path, file_name_without_extension + '.h5'))
        return True
    except:
        print(f"save_keras_sequential: Writing of Sequential as file failed")
        return False


def load_keras_sequential(relative_path: str, filename: str) -> Sequential:
    """
    Loads a Keras Sequential from File System
    
    Args:
        model : Sequential to save
        relative_path : relative path in project
    Returns:
        Sequential, or None if nothing found or error
    """
   
    model_filename_with_path = os.path.join(ROOT_DIR, relative_path, filename + '.json')
    weights_filenme_with_path = os.path.join(ROOT_DIR, relative_path, filename + '.h5')
    
    if os.path.exists(model_filename_with_path) and os.path.exists(weights_filenme_with_path):
        try:             
            json_file = open(model_filename_with_path, 'r')
            loaded_model_json = json_file.read()
            json_file.close()
            model = model_from_json(loaded_model_json)
            model.load_weights(weights_filenme_with_path)
            return model
        except:
            print(f"load_keras_sequential: Loading of Sequential {model_filename_with_path} failed!")
            return None   
    else:
        print(f"load_keras_sequential: model File {model_filename_with_path} or weights file {weights_filenme_with_path} not found!")
        return None

"""
The csv's column keys
"""
DATE, OPEN, HIGH, LOW, CLOSE, ADJ_CLOSE, VOLUME = range(7)
    
def read_stock_market_data(company_enums_and_filenames_tuples: list, path: str = '../datasets/') -> StockMarketData:
    """
    Reads CSV files from "../`path`/`name`.csv" and creates a `StockMarketData` object from this
    :param name: The names of the files to read
    :param path: The path from which to read. Default: "../datasets/"
    :return: The created `StockMarketData` object
    """
    data = {}
    for company_enum, filename in company_enums_and_filenames_tuples:

        filepath = os.path.join(path, filename + '.csv')
        na_portfolio = numpy.loadtxt(filepath, dtype='|S15,f8,f8,f8,f8,f8,i8',
                                     delimiter=',', comments="#", skiprows=1)
        dates = list()
        for day in na_portfolio:
            date = dt.datetime.strptime(day[DATE].decode('UTF-8'), '%Y-%m-%d').date()
            dates.append((date, day[ADJ_CLOSE]))

        data[company_enum] = dates

    return StockMarketData(data)
    
def get_test_data(stock_a, stock_b):
    period1 = '1962-2011'
    period2 = '2012-2017'

    # Reading in *all* available data
    data_a1 = read_stock_market_data([[CompanyEnum.COMPANY_A, ('%s_%s' % (stock_a, period1))]], DATASETS_DIR)
    data_a2 = read_stock_market_data([[CompanyEnum.COMPANY_A, ('%s_%s' % (stock_a, period2))]], DATASETS_DIR)
    data_b1 = read_stock_market_data([[CompanyEnum.COMPANY_B, ('%s_%s' % (stock_b, period1))]], DATASETS_DIR)
    data_b2 = read_stock_market_data([[CompanyEnum.COMPANY_B, ('%s_%s' % (stock_b, period2))]], DATASETS_DIR)

    # Combine both datasets to one StockMarketData object
    old_data_a = data_a1.market_data[CompanyEnum.COMPANY_A]
    new_data_a = data_a2.market_data[CompanyEnum.COMPANY_A]
    old_data_b = data_b1.market_data[CompanyEnum.COMPANY_B]
    new_data_b = data_b2.market_data[CompanyEnum.COMPANY_B]

    full_stock_market_data = StockMarketData({CompanyEnum.COMPANY_A: old_data_a + new_data_a, CompanyEnum.COMPANY_B: old_data_b + new_data_b})

    return full_stock_market_data
