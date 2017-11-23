'''
Created on 08.11.2017

@author: rmueller
'''
from model.IPredictor import IPredictor
import numpy as np

from model.StockData import StockData
from utils import load_keras_sequential, save_keras_sequential, read_stock_market_data
from model.CompanyEnum import CompanyEnum
from logger import logger
from matplotlib import pyplot as plt
from keras.models import Sequential
from definitions import PERIOD_1, PERIOD_2

TEAM_NAME = "team_blue"

RELATIVE_PATH = 'predicting/predictor/' + TEAM_NAME + '/' + TEAM_NAME + '_predictor'
MODEL_FILE_NAME_STOCK_A = TEAM_NAME + '_predictor_stock_a_network'
MODEL_FILE_NAME_STOCK_B = TEAM_NAME + '_predictor_stock_b_network'

# Neural network configuration

#TODO: choose size
INPUT_SIZE = 42
FIRST_LAYER_SIZE = 42 
SECOND_LAYER_SIZE = 42 
OUTPUT_SIZE = 42
ACTIVATION_FUNCTION_FOR_OUTPUT = 'TODO'
LOSS_FUNCTION = 'TODO'
OPTIMIZER = 'TODO'
METRICS = ['TODO']
BATCH_SIZE = 128

class TeamBlueBasePredictor(IPredictor):
    '''
    Predictor based on an already trained neural network.
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
            logger.warn(f"Loading of trained neural network failed, creating a new untrained one.")
            self.trained = False
            self.model = create_model()
            
        self.model.compile(loss=LOSS_FUNCTION, optimizer=OPTIMIZER)
        
    def doPredict(self, data: StockData) -> float:
        """ Use the loaded trained neural network to predict the next stock value.
    
        Args:
          data : historical stock values of a company
        Returns:
          predicted next stock value for that company
        """
        # Extract last 100 floats (here: stock values) as input for neural network (format: numpy array of arrays)
        input_values = np.array([[x[1] for x in data.get_from_offset(-INPUT_SIZE)]])

        try:
            # Let network predict the next stock value based on last INPUT_SIZE stock values
            return self.model.predict(input_values)
        except:
            logger.error("Error in predicting next stock value.")
            assert False


class TeamBlueStockAPredictor(TeamBlueBasePredictor):
    '''
    Predictor for stock A based on an already trained neural network.
    '''

    def __init__(self):
        '''
        Constructor: Load the trained and stored neural network.
        '''
        super().__init__(MODEL_FILE_NAME_STOCK_A)


class TeamBlueStockBPredictor(TeamBlueBasePredictor):
    '''
    Predictor for stock B based on an already trained neural network.
    '''

    def __init__(self):
        '''
        Constructor: Load the trained and stored neural network.
        '''
        super().__init__(MODEL_FILE_NAME_STOCK_B)

###############################################################################
# The following code trains and stores the corresponding neural network
###############################################################################


def learn_nn_and_save(training_data: StockData, test_data: StockData, filename_to_save:str):
    
        
    training_dates = training_data.get_dates()
    training_prices = training_data.get_values()
    test_prices = test_data.get_values()
    
    
    # Build chunks of prices from INPUT_SIZE consecutive days (lastPrices) and 101th day (currentPrice)
    lastPrices, currentPrice = [], []
    for i in range(0, len(training_prices) - INPUT_SIZE):
        lastPrices.append(training_prices[i:INPUT_SIZE + i])
        currentPrice.append(float(training_prices[INPUT_SIZE + i]))

    #the same for test data:
    last_prices_test, current_price_test = [], []
    for i in range(0, len(last_prices_test) - INPUT_SIZE):
        last_prices_test.append(test_prices[i:INPUT_SIZE + i])
        current_price_test.append(float(test_prices[INPUT_SIZE + i]))

    network = create_model()
    
    network.compile(loss=LOSS_FUNCTION, optimizer=OPTIMIZER)

    # Train the neural network
    history = network.fit(lastPrices, currentPrice, epochs=500, batch_size=BATCH_SIZE, verbose=1, validation_data=(last_prices_test, current_price_test), shuffle=True)

    # Evaluate the trained neural network and plot results
    score = network.evaluate(np.array(lastPrices), currentPrice, batch_size=BATCH_SIZE, verbose=0)
    logger.debug(f"Test score: {score}")
                     
    #Draw results
    plt.figure()
    plt.plot(history.history['loss'])
    plt.title('training loss / testing loss by epoch')
    plt.ylabel('loss')
    plt.xlabel('epoch')
    plt.legend(['training', 'testing'], loc='best')
    
    plt.figure()
    currentPrice_prediction = network.predict(lastPrices, batch_size=BATCH_SIZE)
    plt.plot(training_dates[INPUT_SIZE:], currentPrice, color="black")  # current prices in reality
    plt.plot(training_dates[INPUT_SIZE:], currentPrice_prediction, color="green")  # predicted prices by neural network
    plt.title('current prices / predicted prices by date')
    plt.ylabel('price')
    plt.xlabel('date')
    plt.legend(['current', 'predicted'], loc='best')
    
    plt.show()

    # Save trained model: separate network structure (stored as JSON) and trained weights (stored as HDF5)
    save_keras_sequential(network, RELATIVE_PATH, filename_to_save)


def create_model() -> Sequential:
    network = Sequential()
    
    #TODO: add layers
   
    return network

if __name__ == "__main__":
    logger.debug("Data loading...")
    training_stock_market_data = read_stock_market_data([CompanyEnum.COMPANY_A, CompanyEnum.COMPANY_B], [PERIOD_1])
    test_stock_market_data = read_stock_market_data([CompanyEnum.COMPANY_A, CompanyEnum.COMPANY_B], [PERIOD_2])
    
    company_a_StockData = training_stock_market_data[CompanyEnum.COMPANY_A]
    datesA = company_a_StockData.get_dates()
    pricesA = company_a_StockData.get_values()
    
    logger.debug(f"Data for Stock A loaded: {len(pricesA)} prices and {len(datesA)} dates read.")
    learn_nn_and_save(datesA, pricesA, MODEL_FILE_NAME_STOCK_A)
    
    company_b_StockData = training_stock_market_data[CompanyEnum.COMPANY_B]
    datesB = company_b_StockData.get_dates()
    pricesB = company_b_StockData.get_values()
    
    logger.debug(f"Data for Stock B loaded: {len(pricesB)} prices and {len(datesB)} dates read.")
    learn_nn_and_save(datesB, pricesB, MODEL_FILE_NAME_STOCK_B)

