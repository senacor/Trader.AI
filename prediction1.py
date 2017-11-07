# For plotting the results
from matplotlib import pyplot as plt
# For parsing dates from source data
import datetime as dt
# TODO
from keras.models import Sequential
from keras.layers import Dense, Activation, Dropout
# For visualizing the Keras model
from keras.utils import plot_model

# Load source data
print("Data loading...")
dates, prices = [], []
f = open('datasets/GSPC.csv', 'r')
next(f) # skip the header line
for line in f:
    try:
        dates.append(dt.datetime.strptime(line.split(',')[0], '%Y-%m-%d').date()) # save dates in datetime.date format
        prices.append(float(line.split(',')[4])) # save prices in float format
    except:
        print("Error in reading line", line)
f.close()
print("Data loaded:", len(prices), "prices and", len(dates), "dates read.")

# Build chunks of prices from 100 consecutive days (lastPrices) and 101th day (currentPrice)
print("Data splitting...")
lastPrices, currentPrice = [], []
for i in range(0, len(prices)-100):
    lastPrices.append(prices[i:100+i])
    currentPrice.append(prices[100+i])
# Split lastPrices and currentPrice into 80% training data and 20% test data
from sklearn.model_selection import train_test_split
lastPrices_training, lastPrices_test, currentPrice_training, currentPrice_test = train_test_split(lastPrices, currentPrice, test_size=0.2)
assert len(lastPrices) == len(lastPrices_training) + len(lastPrices_test)
assert len(currentPrice) == len(currentPrice_training) + len(currentPrice_test)
print("Data splitted:", len(lastPrices_training), "training tuples and", len(lastPrices_test), "test tuples.")

# Building a neural network
print("Model building...")
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
print("Model built.")

# Training the neural network
print("Model training...")
network.compile(optimizer='adam', loss='mse') # Configures the model for training
# network.fit(lastPrices_training, currentPrice_training, validation_data=(lastPrices_test, currentPrice_test), epochs=5, batch_size=128, verbose=1)
network.fit(lastPrices_training, currentPrice_training, epochs=5, batch_size=128, verbose=1)
print("Model trained.")

print("rein:", lastPrices_training[0])
import numpy as np
input = np.array((lastPrices_training[0],))
expected = network.predict_classes(input, verbose=1)
print("raus:", expected)
print("tatsächliches Ergebnis:", currentPrice_training[0])

# Evaluate the trained neural network
score = network.evaluate(lastPrices_test, currentPrice_test, batch_size=128)
print(score)

# Plot the results
plt.plot(dates, prices)
plt.show()