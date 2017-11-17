'''
Created on 08.11.2017

@author: rmueller
'''
from model.IPredictor import IPredictor
import numpy as np

from utils import load_keras_sequential, save_keras_sequential, read_stock_market_data_conveniently
from model.CompanyEnum import CompanyEnum
from logger import logger
from matplotlib import pyplot as plt
from keras.models import Sequential
from keras.layers import Dense

MODEL_FILE_NAME_STOCK_A = 'stock_a_predictor'
MODEL_FILE_NAME_STOCK_B = 'stock_b_predictor'
RELATIVE_PATH = 'predicting/predictor'

class BaseNnPredictor(IPredictor):
    '''
    Perfect predictor based on an already trained neural network.
    '''

    def __init__(self, nn_filename : str):
        '''
        Constructor: Load the trained and stored neural network.
        '''
        # Try loading a stored trained neural network...
        self.trained = True
        self.model = load_keras_sequential(RELATIVE_PATH, nn_filename)
        # ... if that wasn't possible, then create a new untrained one
        if self.model is None:
            logger.debug(f"BaseNnPredictor: Loading of trained neural network failed, creating a new untrained one.")
            self.trained = False
            self.model = Sequential()
            self.model.add(Dense(500, activation='relu', input_dim=100))
            self.model.add(Dense(500, activation='relu'))
            self.model.add(Dense(1, activation='linear'))
        self.model.compile(loss='mean_squared_error', optimizer='adam')
        
    def doPredict(self, data:list) -> float:
        """ Use the loaded trained neural network to predict the next stock value.
    
        Args:
          data : historical stock values of a company
        Returns:
          predicted next stock value for that company
        """
        # TODO diese Assumptions hier sind Mist, da fehlt uns eine Klasse für
        # Assumptions about data: at least 100 pairs of type (_, float)
        assert len(data) >= 100
        assert len(data[0]) == 2
        assert isinstance(data[0][1], float)

        # Extract last 100 floats (here: stock values) as input for neural network (format: numpy array of arrays)
        input_values = np.array([[x[1] for x in data[-100:]]])

        try:
            # Let network predict the next stock value based on last 100 stock values
            return self.model.predict(input_values)
        except:
            logger.error("Error in predicting next stock value.")
            assert False

class StockANnPredictor(BaseNnPredictor):
    '''
    Perfect predictor for stock A based on an already trained neural network.
    '''
    def __init__(self):
        '''
        Constructor: Load the trained and stored neural network.
        '''
        BaseNnPredictor.__init__(self, MODEL_FILE_NAME_STOCK_A)

class StockBNnPredictor(BaseNnPredictor):
    '''
    Perfect predictor for stock B based on an already trained neural network.
    '''
    def __init__(self):
        '''
        Constructor: Load the trained and stored neural network.
        '''
        BaseNnPredictor.__init__(self, MODEL_FILE_NAME_STOCK_B)

###############################################################################
# The following code trains and stores the corresponding neural network
###############################################################################

def learnNnAndSave(dates: list, prices: list, filename_to_save:str):
    # Build chunks of prices from 100 consecutive days (lastPrices) and 101th day (currentPrice)
    lastPrices, currentPrice = [], []
    for i in range(0, len(prices) - 100):
        lastPrices.append(prices[i:100 + i])
        currentPrice.append(prices[100 + i])

    network = Sequential()
    network.add(Dense(500, activation='relu', input_dim=100))
    network.add(Dense(500, activation='relu'))
    network.add(Dense(1, activation='linear'))
    network.compile(loss='mean_squared_error', optimizer='adam')

    # Train the neural network
    history = network.fit(lastPrices, currentPrice, epochs=10, batch_size=128, verbose=1)

    # Evaluate the trained neural network and plot results
    score = network.evaluate(lastPrices, currentPrice, batch_size=128, verbose=0)
    logger.debug('Test score: ', score)
    plt.figure()
    plt.plot(history.history['loss'])
    plt.title('training loss / testing loss by epoch')
    plt.ylabel('loss')
    plt.xlabel('epoch')
    plt.legend(['training', 'testing'], loc='best')
    plt.figure()
    currentPrice_prediction = network.predict(lastPrices, batch_size=128)
    plt.plot(dates[100:], currentPrice, color="black")  # current prices in reality
    plt.plot(dates[100:], currentPrice_prediction, color="green")  # predicted prices by neural network
    plt.title('current prices / predicted prices by date')
    plt.ylabel('price')
    plt.xlabel('date')
    plt.legend(['current', 'predicted'], loc='best')
    plt.show()

    # Save trained model: separate network structure (stored as JSON) and trained weights (stored as HDF5)
    save_keras_sequential(network, RELATIVE_PATH, filename_to_save)


if __name__ == "__main__":
    # Load the training data; here: complete data about stock A (Disney)
    logger.debug("Data loading...")
    full_stock_market_data = read_stock_market_data_conveniently([CompanyEnum.COMPANY_A, CompanyEnum.COMPANY_B], ['1962-2011', '2012-2017'])
    
    company_a_stock_market_data = full_stock_market_data.get_stock_data_for_company(CompanyEnum.COMPANY_A)
    datesA = np.array([[x[0] for x in company_a_stock_market_data]])[0].tolist()
    pricesA = np.array([[x[1] for x in company_a_stock_market_data]])[0].tolist()
    
    logger.debug("Data for Stock A loaded:", len(pricesA), "prices and", len(datesA), "dates read.")
    learnNnAndSave(datesA, pricesA, MODEL_FILE_NAME_STOCK_A)
    
    company_b_stock_market_data = full_stock_market_data.get_stock_data_for_company(CompanyEnum.COMPANY_B)
    datesB = np.array([[x[0] for x in company_b_stock_market_data]])[0].tolist()
    pricesB = np.array([[x[1] for x in company_b_stock_market_data]])[0].tolist()
    logger.debug("Data for Stock B loaded:", len(pricesB), "prices and", len(datesB), "dates read.")
    learnNnAndSave(datesB, pricesB, MODEL_FILE_NAME_STOCK_B)


