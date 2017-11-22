'''
Created on 15.11.2017

Utility functions

@author: jtymoszuk
'''
import os
from keras.models import Sequential
from keras.models import model_from_json
from definitions import ROOT_DIR, DATASETS_DIR
from model.StockData import StockData
from model.StockMarketData import StockMarketData
import numpy
from model.CompanyEnum import CompanyEnum
import datetime as dt
from typing import List, Dict, Tuple
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

        model_filename_with_path = os.path.join(ROOT_DIR, relative_path, file_name_without_extension + '.json')
        weights_filename_with_path = os.path.join(ROOT_DIR, relative_path, file_name_without_extension + '.h5')

        json_file = open(model_filename_with_path, "w")
        json_file.write(model_as_json)
        json_file.close()

        model.save_weights(weights_filename_with_path)
        logger.info(f"save_keras_sequential: Saved Sequential from {model_filename_with_path} "
                    f"and {weights_filename_with_path}!")
        return True
    except:
        logger.error(f"save_keras_sequential: Writing of Sequential as file failed")
        return False


def load_keras_sequential(relative_path: str, file_name_without_extension: str) -> Sequential:
    """
    Loads a Keras Sequential neural network from file system
    
    Args:
        relative_path : relative path in project
        file_name_without_extension : file name without extension, will be used for json with models and h5 with weights.
    Returns:
        Sequential, or None if nothing found or error
    """

    model_filename_with_path = os.path.join(ROOT_DIR, relative_path, file_name_without_extension + '.json')
    weights_filename_with_path = os.path.join(ROOT_DIR, relative_path, file_name_without_extension + '.h5')

    if os.path.exists(model_filename_with_path) and os.path.exists(weights_filename_with_path):
        try:
            json_file = open(model_filename_with_path, 'r')
            loaded_model_json = json_file.read()
            json_file.close()
            model = model_from_json(loaded_model_json)
            model.load_weights(weights_filename_with_path)
            logger.info(f"load_keras_sequential: Loaded Sequential from {model_filename_with_path} "
                        f"and {weights_filename_with_path}!")
            return model
        except:
            logger.error(f"load_keras_sequential: Loading of Sequential {model_filename_with_path} failed!")
            return None
    else:
        logger.error(f"load_keras_sequential: model File {model_filename_with_path} "
                     f"or weights file {weights_filename_with_path} not found!")
        return None


StockList = List[CompanyEnum]
PeriodList = List[str]


def read_stock_market_data(stocks: StockList, periods: PeriodList) -> StockMarketData:
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
            * 'stock_a_2012-2015.csv'
            * 'stock_b_1962-2011.csv'
            * 'stock_b_2012-2015.csv'
          into a dict with keys `CompanyEnum.COMPANY_A` and `CompanyEnum.COMPANY_B` respectively
        * `(['stock_a'], ['1962-2011', '2012-2017'])` reads:
            * 'stock_a_1962-2011.csv'
            * 'stock_a_2012-2015.csv'
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
            data[stock] = StockData(__read_stock_market_data([[stock, filename]])[stock])
        else:
            period_data = list()
            for period in periods:
                period_data.append(__read_stock_market_data([[stock, ('%s_%s' % (filename, period))]]))
            data[stock] = StockData(
                [item for period_dict in period_data if period_dict is not None for item in period_dict[stock]])

    return StockMarketData(data)


"""
The csv's column keys
"""
DATE, OPEN, HIGH, LOW, CLOSE, ADJ_CLOSE, VOLUME = range(7)


def __read_stock_market_data(names_and_filenames: list) -> Dict[CompanyEnum, List[Tuple[dt.datetime.date, float]]]:
    """
    Reads CSV files from "../`DATASETS_DIR`/`name`.csv" and creates a `StockMarketData` object from this

    Args:
        names_and_filenames: Tuples of filenames and logical names used as dict keys

    Returns:
        A dict. Structure: { CompanyEnum: List[Tuple[dt.datetime.date, float]] }
    """
    data = {}
    for company_enum, filename in names_and_filenames:
        filepath = os.path.join(DATASETS_DIR, filename + '.csv')

        if not os.path.exists(filepath):
            continue

        na_portfolio = numpy.loadtxt(filepath, dtype='|S15,f8,f8,f8,f8,f8,i8',
                                     delimiter=',', comments="#", skiprows=1)
        dates = list()
        for day in na_portfolio:
            date = dt.datetime.strptime(day[DATE].decode('UTF-8'), '%Y-%m-%d').date()
            dates.append((date, day[ADJ_CLOSE]))

        data[company_enum] = dates

    return data if len(data) > 0 else None
