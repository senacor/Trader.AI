"""
Created on 08.11.2017

@author: rmueller
"""
from model.IPredictor import IPredictor
import numpy as np

from model.StockData import StockData
from utils import load_keras_sequential, save_keras_sequential, read_stock_market_data
from model.CompanyEnum import CompanyEnum
from logger import logger
from matplotlib import pyplot as plt
from keras.models import Sequential
from keras.layers import Dense

RELATIVE_PATH = 'predicting/predictor/reference/nn_value_predictor'
MODEL_FILE_NAME_STOCK_A = 'nn_value_predictor_stock_a_network'
MODEL_FILE_NAME_STOCK_B = 'nn_value_predictor_stock_b_network'


class BaseNnValuePredictor(IPredictor):
    """
    Perfect predictor based on an already trained neural network.
    """

    def __init__(self, nn_filename: str):
        """
        Constructor: Load the trained and stored neural network.

        Args:
            nn_filename: The filename to load the trained data from
        """
        # Try loading a stored trained neural network...
        self.trained = True
        self.model = load_keras_sequential(RELATIVE_PATH, nn_filename)
        # ... if that wasn't possible, then create a new untrained one
        if self.model is None:
            logger.warn(f"Loading of trained neural network failed, creating a new untrained one.")
            self.trained = False
            self.model = create_model()

        self.model.compile(loss='mean_squared_error', optimizer='adam')

    def doPredict(self, data: StockData) -> float:
        """ Use the loaded trained neural network to predict the next stock value.
    
        Args:
          data: The historical stock values of a company

        Returns:
          The predicted next stock value for that company
        """
        # Assumptions about data: at least 100 pairs of type (_, float)
        assert data is not None and data.get_row_count() >= 100

        # Extract last 100 floats (here: stock values) as input for neural network (format: numpy array of arrays)
        input_values = np.array([[x[1] for x in data.get_from_offset(-100)]])

        try:
            # Let network predict the next stock value based on last 100 stock values
            return self.model.predict(input_values)
        except:
            logger.error("Error in predicting next stock value.")
            assert False


class StockANnValuePredictor(BaseNnValuePredictor):
    """
    Perfect predictor for stock A based on an already trained neural network.
    """

    def __init__(self):
        """
        Constructor: Load the trained and stored neural network.
        """
        super().__init__(MODEL_FILE_NAME_STOCK_A)


class StockBNnValuePredictor(BaseNnValuePredictor):
    """
    Perfect predictor for stock B based on an already trained neural network.
    """

    def __init__(self):
        """
        Constructor: Load the trained and stored neural network.
        """
        super().__init__(MODEL_FILE_NAME_STOCK_B)


###############################################################################
# The following code trains and stores the corresponding neural network
###############################################################################

def learn_nn_and_save(data: StockData, filename_to_save: str):
    """
    Starts the training of the neural network and saves it to the file system

    Args:
        data: The data to train on
        filename_to_save: The filename to save the trained NN to
    """
    dates = data.get_dates()
    prices = data.get_values()

    # Generate training data
    # Build chunks of prices from 100 consecutive days (last_prices) and 101th day (current_price)
    last_prices, current_price = [], []
    for i in range(0, len(prices) - 100):
        last_prices.append(prices[i:100 + i])
        current_price.append(float(prices[100 + i]))

    network = create_model()

    network.compile(loss='mean_squared_error', optimizer='adam')

    # Train the neural network
    history = network.fit(last_prices, current_price, epochs=10, batch_size=128, verbose=1)

    # Evaluate the trained neural network and plot results
    score = network.evaluate(np.array(last_prices), current_price, batch_size=128, verbose=0)
    logger.debug(f"Test score: {score}")
    plt.figure()
    plt.plot(history.history['loss'])
    plt.title('training loss / testing loss by epoch')
    plt.ylabel('loss')
    plt.xlabel('epoch')
    plt.legend(['training', 'testing'], loc='best')
    plt.figure()
    current_price_prediction = network.predict(last_prices, batch_size=128)
    plt.plot(dates[100:], current_price, color="black")  # current prices in reality
    plt.plot(dates[100:], current_price_prediction, color="green")  # predicted prices by neural network
    plt.title('current prices / predicted prices by date')
    plt.ylabel('price')
    plt.xlabel('date')
    plt.legend(['current', 'predicted'], loc='best')
    plt.show()

    # Save trained model: separate network structure (stored as JSON) and trained weights (stored as HDF5)
    save_keras_sequential(network, RELATIVE_PATH, filename_to_save)


def create_model() -> Sequential:
    network = Sequential()
    network.add(Dense(500, activation='relu', input_dim=100))
    network.add(Dense(500, activation='relu'))
    network.add(Dense(1, activation='linear'))

    return network


if __name__ == "__main__":
    # Load the training data; here: complete data about stock A
    logger.debug("Data loading...")
    full_stock_market_data = read_stock_market_data([CompanyEnum.COMPANY_A, CompanyEnum.COMPANY_B],
                                                    ['1962-2011', '2012-2017'])

    company_a_stock_data = full_stock_market_data[CompanyEnum.COMPANY_A]

    logger.debug(f"Data for Stock A loaded: {company_a_stock_data.get_row_count()} prices and dates read.")
    learn_nn_and_save(company_a_stock_data, MODEL_FILE_NAME_STOCK_A)

    company_b_stock_data = full_stock_market_data[CompanyEnum.COMPANY_B]

    logger.debug(f"Data for Stock B loaded: {company_b_stock_data.get_row_count()} prices and dates read.")
    learn_nn_and_save(company_b_stock_data, MODEL_FILE_NAME_STOCK_B)
