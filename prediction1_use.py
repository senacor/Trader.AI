# For plotting the results
from matplotlib import pyplot as plt
# For parsing dates from source data
import datetime as dt
# For loading the trained neural network
from keras.models import model_from_json

# Load the network structure (JSON file) and the trained weights (HDF5 file)
print("Model loading...")
json_file = open('prediction1_structure.json', 'r')
loaded_model_json = json_file.read()
json_file.close()
network = model_from_json(loaded_model_json)
network.load_weights('prediction1_weights.h5')
print("Model loaded.")

# Load the input data and split into chunks of 100 days
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

lastPrices, currentPrice = [], []
for i in range(0, len(prices)-100):
    lastPrices.append(prices[i:100+i])
    currentPrice.append(prices[100+i])

# Use trained network to predict prices
plt.figure() # Show last 100 current prices vs. predicted prices
currentPrice_prediction = network.predict(lastPrices, batch_size=128)
plt.plot(dates[100:], currentPrice, color="black") # current prices in reality
plt.plot(dates[100:], currentPrice_prediction, color="green") # predicted prices by neural network
plt.title('current prices / predicted prices by date')
plt.ylabel('price')
plt.xlabel('date')
plt.legend(['current', 'predicted'], loc='best')
plt.show()