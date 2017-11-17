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
from typing import List
from logger import logger


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
        logger.error(f"save_keras_sequential: Writing of Sequential as file failed")
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
            logger.error(f"load_keras_sequential: Loading of Sequential {model_filename_with_path} failed!")
            return None   
    else:
        logger.error(f"load_keras_sequential: model File {model_filename_with_path} or weights file {weights_filenme_with_path} not found!")
        return None


"""
The csv's column keys
"""
DATE, OPEN, HIGH, LOW, CLOSE, ADJ_CLOSE, VOLUME = range(7)
    
def read_stock_market_data(company_enums_and_filenames_tuples: list, path: str='../datasets/') -> StockMarketData:
    """
    Reads CSV files from "../`path`/`name`.csv" and creates a `StockMarketData` object from this

    Args:
        company_enums_and_filenames_tuples: Tuples of filenames and logical names used as dict keys
        path: The path from which to read. Default: "../datasets/"

    Returns:
        The created `StockMarketData` object
    """
    data = {}
    for company_enum, filename in company_enums_and_filenames_tuples:

        filepath = os.path.join(path, filename + '.csv')
        
        assert os.path.exists(filepath)
        
        na_portfolio = numpy.loadtxt(filepath, dtype='|S15,f8,f8,f8,f8,f8,i8',
                                     delimiter=',', comments="#", skiprows=1)
        dates = list()
        for day in na_portfolio:
            date = dt.datetime.strptime(day[DATE].decode('UTF-8'), '%Y-%m-%d').date()
            dates.append((date, day[ADJ_CLOSE]))

        data[company_enum] = dates

    return StockMarketData(data)


StockList = List[CompanyEnum]
PeriodList = List[str]  


def read_stock_market_data_conveniently(stocks: StockList, periods: PeriodList) -> StockMarketData:
    """
    Reads the "cross product" from `stocks` and `periods` from CSV files and creates a `StockMarketData` object from
    this. For each defined stock in `stocks` the corresponding value from `CompanyEnum` is used as logical name. If
    there are `periods` provided those are each read.

    Args:
        stocks: The company names for which to read the stock data. *Important:* These values need to be stated in `CompanyEnum`
        periods: The periods to read. If not empty each period is appended to the filename like this: `[stock_name]_[period].csv`

    Returns:
        The created `StockMarketData` object

    Examples:
        * Preface: Provided stock names are supposed to be part to `CompanyEnum`. They are stated plaintext-ish here to show the point:
        * `(['stock_a', 'stock_b'], ['1962-2011', '2012-2017'])` reads:
            * 'stock_a_1962-2011.csv'
            * 'stock_a_2012-2017.csv'
            * 'stock_b_1962-2011.csv'
            * 'stock_b_2012-2017.csv'
          into a dict with keys `CompanyEnum.COMPANY_A` and `CompanyEnum.COMPANY_B` respectively
        * `(['stock_a'], ['1962-2011', '2012-2017'])` reads:
            * 'stock_a_1962-2011.csv'
            * 'stock_a_2012-2017.csv'
          into a dict with a key `CompanyEnum.COMPANY_A`
        * `(['stock_a', 'stock_b'], ['1962-2011'])` reads:
            * 'stock_a_1962-2011.csv'
            * 'stock_b_1962-2011.csv'
          into a dict with keys `CompanyEnum.COMPANY_A` and `CompanyEnum.COMPANY_B` respectively
        * `(['stock_a', 'stock_b'], [])` reads:
            * 'stock_a.csv'
            * 'stock_b.csv'
          into a dict with keys `CompanyEnum.COMPANY_A` and `CompanyEnum.COMPANY_B` respectively

    """
    data = dict()

    # Read *all* available data
    for stock in stocks:
        filename = stock.value
        if len(periods) is 0:
            data[stock] = read_stock_market_data([[stock, filename]], DATASETS_DIR)
        else:
            period_data = list()
            for period in periods:
                period_data.append(read_stock_market_data([[stock, ('%s_%s' % (filename, period))]], DATASETS_DIR))
            data[stock] = [item for sublist in period_data for item in sublist.market_data[stock]]

    return StockMarketData(data)

