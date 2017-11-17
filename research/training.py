
import numpy as np
from sklearn import preprocessing
from sklearn.metrics import mean_squared_error, classification_report
import matplotlib.pylab as plt
from logger import logger
import time

import datetime

# from keras.models import Sequential, Graph
from keras.callbacks import Callback
from keras.layers.core import Dense, Dropout, Activation
from keras.models import Sequential
from keras.utils import plot_model

from processing import *

class TrainingHistory(Callback):
    def on_train_begin(self, logs={}):
        self.losses = []
        self.accuracy = []
        self.predictions = []
        self.i = 0
        self.save_every = 5000

    def on_batch_end(self, batch, logs={}):
        self.losses.append(logs.get('loss'))
        self.accuracy.append(logs.get('acc'))
        self.i += 1
        if self.i % self.save_every == 0:
            pred = model.predict(X_train)
            self.predictions.append(pred)


logger.debug('Data loading...')
timeseries, dates = load_snp_close()
dates = [datetime.datetime.strptime(d, '%Y-%m-%d').date() for d in dates]
plt.plot(dates, timeseries)

TRAIN_SIZE = 100
TARGET_TIME = 1
LAG_SIZE = 1
EMB_SIZE = 1

X, Y = split_into_chunks(timeseries, TRAIN_SIZE, TARGET_TIME, LAG_SIZE, binary=False, scale=True)
X, Y = np.array(X), np.array(Y)
X_train, X_test, Y_train, Y_test = create_Xt_Yt(X, Y, percentage=0.9)

Xp, Yp = split_into_chunks(timeseries, TRAIN_SIZE, TARGET_TIME, LAG_SIZE, binary=False, scale=False)
Xp, Yp = np.array(Xp), np.array(Yp)
X_trainp, X_testp, Y_trainp, Y_testp = create_Xt_Yt(Xp, Yp, percentage=0.9)

logger.debug('Building model...')
model = Sequential()
model.add(Dense(500, input_shape=(TRAIN_SIZE,)))
model.add(Activation('relu'))
model.add(Dropout(0.25))
model.add(Dense(250))
model.add(Activation('relu'))
model.add(Dense(1))
model.add(Activation('linear'))
model.compile(optimizer='adam', loss='mse')

logger.debug(f"X_train.shape: {X_train.shape}")
logger.debug(f"Y_train.shape: {Y_train.shape}")

logger.debug("Training......")
model.fit(X_train, Y_train, nb_epoch=5, batch_size=128, verbose=1, validation_split=0.1)
score = model.evaluate(X_test, Y_test, batch_size=128)
logger.debug(f"Score: {score}")

params = []
for xt in X_testp:
    xt = np.array(xt)
    mean_ = xt.mean()
    scale_ = xt.std()
    params.append([mean_, scale_])

predicted = model.predict(X_test)
new_predicted = []

for pred, par in zip(predicted, params):
    a = pred * par[1]
    a += par[0]
    new_predicted.append(a)

mse = mean_squared_error(predicted, new_predicted)
logger.debug(f"mean_squared_error: {mse}")

try:
    fig = plt.figure()
    plt.plot(Y_test[:150], color='black')  # BLUE - trained RESULT
    plt.plot(predicted[:150], color='blue')  # RED - trained PREDICTION
    plt.plot(Y_testp[:150], color='green')  # GREEN - actual RESULT
    plt.plot(new_predicted[:150], color='red')  # ORANGE - restored PREDICTION
    plt.show()
    
except Exception as e:
    logger.error(str(e))
    
plot_model(model, to_file='model.png', show_shapes=True)
