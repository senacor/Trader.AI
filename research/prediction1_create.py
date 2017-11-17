# For plotting the results
from matplotlib import pyplot as plt
# For parsing dates from source data
import datetime as dt
# TODO
from keras.models import Sequential
from keras.layers import Dense, Activation, Dropout
# For visualizing the Keras model
from keras.utils import plot_model
from logger import logger

# Load source data
logger.debug("Data loading...")
dates, prices = [], []
f = open('datasets/^DJT.csv', 'r')
next(f) # skip the header line
for line in f:
    try:
        dates.append(dt.datetime.strptime(line.split(',')[0], '%Y-%m-%d').date()) # save dates in datetime.date format
        prices.append(float(line.split(',')[4])) # save prices in float format
    except:
        logger.error("Error in reading line", line)
f.close()
# plt.plot(dates, prices)
# plt.show()
logger.debug("Data loaded:", len(prices), "prices and", len(dates), "dates read.")

# Build chunks of prices from 100 consecutive days (lastPrices) and 101th day (currentPrice)
logger.debug("Data splitting...")
lastPrices, currentPrice = [], []
from sklearn import preprocessing
for i in range(0, len(prices)-100):
    # scaledLastPrices = preprocessing.scale(prices[i:101+i])
    # assert len(scaledLastPrices) == 101
    lastPrices.append(prices[i:100+i])
    currentPrice.append(prices[100+i])
    # lastPrices.append(scaledLastPrices[:100])
    # currentPrice.append(scaledLastPrices[100])
# Split lastPrices and currentPrice into 80% training data and 20% test data
from sklearn.model_selection import train_test_split
lastPrices_training, lastPrices_test, currentPrice_training, currentPrice_test = train_test_split(lastPrices, currentPrice, test_size=0.2)
# assert len(lastPrices) == len(lastPrices_training) + len(lastPrices_test)
# assert len(currentPrice) == len(currentPrice_training) + len(currentPrice_test)
logger.debug("Data splitted:", len(lastPrices_training), "training tuples and", len(lastPrices_test), "test tuples.")

# Building a neural network
logger.debug("Model building...")
network = Sequential() # create Sequential model
# Dense(500) is a fully-connected layer with 500 hidden units.
# in the first layer, you must specify the expected input data shape: here, 100-dimensional vectors.
# Activation applies an activation function to an output
network.add(Dense(500, activation='relu', input_dim=100))
network.add(Dropout(0.25)) # applies Dropout to the input
network.add(Dense(250, activation='relu'))
network.add(Dense(1, activation='linear'))
# network.summary() # prints out summary representation of model
# plot_model(network, to_file='model.png', show_shapes=True, show_layer_names=True)
logger.debug("Model built.")

# Configure and train the neural network
logger.debug("Model training...")
network.compile(loss='mean_squared_error', optimizer='adam')
history = network.fit(lastPrices_training, currentPrice_training, validation_data=(lastPrices_test, currentPrice_test), epochs=5, batch_size=128, verbose=1)
logger.debug("Model trained.")

# Evaluate the trained neural network and plot results
logger.debug("Model evaluating...")
score = network.evaluate(lastPrices_test, currentPrice_test, batch_size=128, verbose=0)
logger.debug('Test score: ', score)
plt.figure() # Show training loss vs. testing loss
plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.title('training loss / testing loss by epoch')
plt.ylabel('loss')
plt.xlabel('epoch')
plt.legend(['training', 'testing'], loc='best')
plt.figure() # Show last 100 current prices vs. predicted prices
currentPrice_prediction = network.predict(lastPrices, batch_size=128)
plt.plot(dates[100:], currentPrice, color="black") # current prices in reality
plt.plot(dates[100:], currentPrice_prediction, color="green") # predicted prices by neural network
plt.title('current prices / predicted prices by date')
plt.ylabel('price')
plt.xlabel('date')
plt.legend(['current', 'predicted'], loc='best')
plt.show()
logger.debug("Model evaluated.")

# Save trained model: separate network structure (stored as JSON) and trained weights (stored as HDF5)
logger.debug("Model saving...")
model_json = network.to_json()
with open("prediction1_structure.json", "w") as json_file:
    json_file.write(model_json)
network.save_weights("prediction1_weights.h5")
logger.debug("Model saved.")
