'''
Created on 08.11.2017

@author: rmueller
'''
from predicting.predictor_interface import IPredictor
from keras.models import model_from_json
import numpy as np

import os
from definitions import ROOT_DIR
from definitions import DATASETS_DIR


class PerfectStockAPredictor(IPredictor):
    '''
    Simple Predicator always returning last value form given input vector.
    '''

    def __init__(self):
        '''
        Constructor: Load the trained and stored neural network.
        '''
        # TODO use other concept for paths
        json_file = open(os.path.join(ROOT_DIR, 'predicting', 'perfect_stock_a_predictor.json'), 'r')
        loaded_model_json = json_file.read()
        json_file.close()
        self.network = model_from_json(loaded_model_json)
        self.network.load_weights(os.path.join(ROOT_DIR, 'predicting', 'perfect_stock_a_predictor.h5'))
        self.network.compile(loss='mean_squared_error', optimizer='adam')
        
    def doPredict(self, data:list) -> float:
        """ Use the loaded trained neural network to predict the next stock value.
    
        Args:
          data : historical stock values of a company 
        Returns:
          last value from input
        """
        # Our trained neural network takes 100 floats as input
        assert len(data) >= 100
        dataAsArray = np.array(data)
        inputForNetwork = dataAsArray[:, [1]]
        inputForNetwork100 = inputForNetwork[:100]
        inputForNetwork100 = np.reshape(inputForNetwork100, (1, 100))

        try:
            return self.network.predict(inputForNetwork100, batch_size=128)
        except:
            print("Error in predicting next stock value.")
            assert False

###############################################################################
# The following code trains and stores the corresponding neural network
###############################################################################


if __name__ == "__main__":
    # Necessary imports
    import datetime as dt
    from matplotlib import pyplot as plt
    from keras.models import Sequential
    from keras.layers import Dense

    # Load the training data; here: complete data about stock A (Disney)
    print("Data loading...")
    dates, prices = [], []
    f = open(os.path.join(DATASETS_DIR, 'DIS.csv'), 'r')
    next(f)  # skip the header line
    for line in f:
        try:
            dates.append(dt.datetime.strptime(line.split(',')[0], '%Y-%m-%d').date())  # save dates in datetime.date format
            prices.append(float(line.split(',')[4]))  # save prices in float format
        except:
            print("Error in reading line", line)
    f.close()
    print("Data loaded:", len(prices), "prices and", len(dates), "dates read.")

    # Build chunks of prices from 100 consecutive days (lastPrices) and 101th day (currentPrice)
    lastPrices, currentPrice = [], []
    for i in range(0, len(prices) - 100):
        lastPrices.append(prices[i:100 + i])
        currentPrice.append(prices[100 + i])

    # Building a neural network
    network = Sequential()
    network.add(Dense(500, activation='relu', input_dim=100))
    network.add(Dense(500, activation='relu'))
    network.add(Dense(1, activation='linear'))

    # Configure and train the neural network
    network.compile(loss='mean_squared_error', optimizer='adam')
    history = network.fit(lastPrices, currentPrice, epochs=5, batch_size=128, verbose=1)

    # Evaluate the trained neural network and plot results
    score = network.evaluate(lastPrices, currentPrice, batch_size=128, verbose=0)
    print('Test score: ', score)
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
    with open("perfect_stock_a_predictor.json", "w") as json_file:
        json_file.write(network.to_json())
    network.save_weights("perfect_stock_a_predictor.h5")
