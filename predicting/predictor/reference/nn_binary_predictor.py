"""
Created on 08.11.2017

@author: rmueller
"""
from model.IPredictor import IPredictor
import numpy as np

from model.StockData import StockData
from predicting.predictor.reference.predictor_utils import create_model, LOSS_FUNCTION, OPTIMIZER, METRICS, \
    calculate_delta, get_data, INPUT_SIZE
from utils import load_keras_sequential, save_keras_sequential, read_stock_market_data
from model.CompanyEnum import CompanyEnum
from logger import logger
from matplotlib import pyplot as plt
from keras.callbacks import ReduceLROnPlateau
from definitions import PERIOD_1, PERIOD_2, PERIOD_3

MODEL_FILE_NAME_STOCK_A = 'nn_binary_predictor_stock_a_network'
MODEL_FILE_NAME_STOCK_B = 'nn_binary_predictor_stock_b_network'
RELATIVE_PATH = 'predicting/predictor/reference/nn_binary_predictor_data'


class BaseNnBinaryPredictor(IPredictor):
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
            logger.warn(f"BaseNnPredictor: Loading of trained neural network failed, creating a new untrained one.")
            self.trained = False
            self.model = create_model()

        self.model.compile(loss=LOSS_FUNCTION, optimizer=OPTIMIZER, metrics=METRICS)

    def doPredict(self, data: StockData) -> float:
        """
        Use the loaded trained neural network to predict the next stock value.
    
        Args:
          data: The historical stock values of a company

        Returns:
          The predicted next stock value for that company
        """
        # Assumptions about data: at least INPUT_SIZE pairs of type (_, float)
        assert data is not None and data.get_row_count() >= INPUT_SIZE

        # Extract last INPUT_SIZE floats (here: stock values) as input for neural network
        # (format: numpy array of arrays)
        input_values = np.array([[x[1] for x in data.get_from_offset(-INPUT_SIZE)]])

        normalized_prices = []

        vector_min = np.min(input_values)
        vector_max = np.max(input_values)

        for price in input_values:
            normalized_prices.append((price - vector_min) / (vector_max - vector_min))

        input_values = np.asarray(normalized_prices)

        try:
            # Let network predict the next stock value based on last 100 stock values
            prediction = self.model.predict(input_values)[0][0]
            return data.get_last()[1] + calculate_delta(prediction)
        except:
            logger.error("Error in predicting next stock value.")
            assert False


class StockANnBinaryPredictor(BaseNnBinaryPredictor):
    """
    Perfect predictor for stock A based on an already trained neural network.
    """

    def __init__(self):
        """
        Constructor: Load the trained and stored neural network.
        """
        super().__init__(MODEL_FILE_NAME_STOCK_A)


class StockBNnBinaryPredictor(BaseNnBinaryPredictor):
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


def learn_nn_and_save(training_data: StockData, test_data: StockData, filename_to_save: str):
    """
    Starts the training of the neural network and saves it to the file system

    Args:
        training_data: The data to train on
        test_data: The data to test on
        filename_to_save: The filename to save the trained NN to
    """
    training_dates = training_data.get_dates()
    training_prices = training_data.get_values()

    # Generate training data
    # Build chunks of prices from 100 consecutive days (input_training_prices) and 101th day (current_prices_for_plot)
    current_training_prices_for_plot, input_training_prices, wanted_training_results = get_data(training_prices)

    # Generate test data
    test_prices = test_data.get_values()
    current_test_prices_for_plot, input_test_prices, wanted_test_results = get_data(test_prices)

    # Shape and configuration of network is optimized for binary classification problems
    # see: https://keras.io/getting-started/sequential-model-guide/
    network = create_model()

    network.compile(optimizer=OPTIMIZER, loss=LOSS_FUNCTION, metrics=METRICS)

    # Train the neural network
    reduce_lr = ReduceLROnPlateau(monitor='val_loss', factor=0.9, patience=5, min_lr=0.000001, verbose=1)
    history = network.fit(input_training_prices, wanted_training_results, epochs=500, batch_size=128, verbose=1,
                          validation_data=(input_test_prices, wanted_test_results), shuffle=True, callbacks=[reduce_lr])

    # Evaluate the trained neural network and plot results
    score = network.evaluate(input_training_prices, wanted_training_results, batch_size=128, verbose=0)
    logger.debug(f"Test score: {score}")

    # Draw
    plt.figure()
    plt.plot(history.history['loss'])
    plt.plot(history.history['val_loss'])
    plt.plot(history.history['acc'])
    plt.title('training loss / testing loss by epoch')
    plt.ylabel('loss/acc')
    plt.xlabel('epoch')
    plt.legend(['loss', 'val_loss', 'acc'], loc='best')
    plt.figure()
    current_price_prediction = network.predict(input_training_prices, batch_size=128)

    logger.debug(f"current_price_prediction:")
    iteration = 0
    for x in current_price_prediction:
        logger.debug(f"iteration {iteration} - output: {x}")
        iteration = iteration + 1

    plt.plot(training_dates[INPUT_SIZE:], current_training_prices_for_plot, color="black")  # current prices in reality
    plt.plot(training_dates[INPUT_SIZE:], [calculate_delta(x) for x in current_price_prediction],
             color="green")  # predicted prices by neural network
    plt.title('current prices / predicted prices by date')
    plt.ylabel('price')
    plt.xlabel('date')
    plt.legend(['current', 'predicted'], loc='best')
    plt.show()

    # Save trained model: separate network structure (stored as JSON) and trained weights (stored as HDF5)
    save_keras_sequential(network, RELATIVE_PATH, filename_to_save)


if __name__ == "__main__":
    # Load the training data; here: complete data about stock A
    logger.debug("Data loading...")
    training_stock_market_data = read_stock_market_data([CompanyEnum.COMPANY_A, CompanyEnum.COMPANY_B],
                                                        [PERIOD_1, PERIOD_2])
    test_stock_market_data = read_stock_market_data([CompanyEnum.COMPANY_A, CompanyEnum.COMPANY_B], [PERIOD_3])

    company_a_training_stock_data: StockData = training_stock_market_data[CompanyEnum.COMPANY_A]
    company_a_test_stock_data: StockData = test_stock_market_data[CompanyEnum.COMPANY_A]

    logger.debug(f"Data for Stock A loaded")
    learn_nn_and_save(company_a_training_stock_data, company_a_test_stock_data, MODEL_FILE_NAME_STOCK_A)

    company_b_training_stock_data: StockData = training_stock_market_data[CompanyEnum.COMPANY_B]
    company_b_test_stock_data: StockData = test_stock_market_data[CompanyEnum.COMPANY_B]

    logger.debug(f"Data for Stock B loaded")
    learn_nn_and_save(company_b_training_stock_data, company_b_test_stock_data, MODEL_FILE_NAME_STOCK_B)
