from typing import List

import numpy as np
from keras import Sequential
from keras.layers import Dense, BatchNormalization, LeakyReLU

# Neural network configuration
INPUT_SIZE = 400
FIRST_LAYER_SIZE = 200
SECOND_LAYER_SIZE = 20
OUTPUT_SIZE = 1
ACTIVATION_FUNCTION_FOR_OUTPUT = 'sigmoid'
LOSS_FUNCTION = 'binary_crossentropy'
OPTIMIZER = 'rmsprop'
METRICS = ['accuracy']


def get_data(prices: List[float]):
    """
    Generates training or test data for the given `prices`
    Args:
        prices: The prices to generate training or test data from

    Returns:
        Three lists:
         * current_prices_for_plot
         * input_prices
         * wanted_results
    """

    input_prices, current_prices_for_plot, wanted_results = [], [], []

    for i in range(0, len(prices) - INPUT_SIZE):
        last_price_vector = prices[i:INPUT_SIZE + i]

        normalized_prices = []

        vector_min = np.min(last_price_vector)
        vector_max = np.max(last_price_vector)

        for price in last_price_vector:
            normalized_prices.append((price - vector_min) / (vector_max - vector_min))

        last_price_vector = normalized_prices

        input_prices.append(last_price_vector)

        current_price = prices[INPUT_SIZE + i]
        current_prices_for_plot.append(current_price)

        previous_price = prices[INPUT_SIZE + i - 1]

        delta = (current_price - previous_price)

        direction = 0.5
        if delta <= -0.0000001:
            # Sell
            direction = 0.0
        elif delta >= 0.0000001:
            # Buy
            direction = 1.0

        wanted_results.append(direction)

    return current_prices_for_plot, input_prices, wanted_results


def create_model() -> Sequential:
    # Shape and configuration of network is optimized for binary classification problems
    # see: https://keras.io/getting-started/sequential-model-guide/
    """
    Creates a neural network model

    Returns:
        The created network
    """
    network = Sequential()

    # Input layer and first hidden layer
    network.add(Dense(FIRST_LAYER_SIZE, input_dim=INPUT_SIZE))
    network.add(BatchNormalization())
    network.add(LeakyReLU())

    # Second hidden layer
    network.add(Dense(SECOND_LAYER_SIZE))
    network.add(BatchNormalization())
    network.add(LeakyReLU())

    # Output layer
    network.add(Dense(OUTPUT_SIZE, activation=ACTIVATION_FUNCTION_FOR_OUTPUT))

    return network


def calculate_delta(nn_output) -> float:
    """
    Normalizes values to 1.0, 0 or -1.0. If `nn_output` is in (0.4...0.6) 0.0 is returned. If it is greater or lower
    1.0 and -1.0 is returned respectively

    Args:
        nn_output: The value to normalize

    Returns:
        The normalized value
    """
    if nn_output > 0.6:
        return 1.0
    elif nn_output < 0.4:
        return -1.0
    else:
        return 0.0
