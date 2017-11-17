import numpy as np
from keras.models import Sequential, model_from_json
from keras.layers import Dense
from keras.optimizers import Adam
from logger import logger

state_size = 2
action_size = 1
hidden_size = 1
learning_rate = 0.001

old_model = Sequential()
old_model.add(Dense(hidden_size, input_dim=state_size, activation='relu', kernel_initializer='he_uniform'))
old_model.compile(loss='mse', optimizer=Adam(lr=learning_rate))

# Save model
model_json = old_model.to_json()
with open("keras_load_save_weights.json", "w") as json_file:
    json_file.write(model_json)
old_model.save_weights("keras_load_save_weights.h5")

# Load model
json_file = open('keras_load_save_weights.json', 'r')
loaded_model_json = json_file.read()
json_file.close()
new_model = model_from_json(loaded_model_json)
new_model.load_weights('keras_load_save_weights.h5')
new_model.compile(loss='mse', optimizer=Adam(lr=learning_rate))

# Compare weights
old_weights = np.array(old_model.get_weights())
logger.debug(old_weights)
logger.debug(old_weights.shape)
new_weights = np.array(new_model.get_weights())
logger.debug(new_weights)
logger.debug(new_weights.shape)

logger.debug(f"compare all dimensions: {np.all(old_weights == new_weights)}")
for i in range(len(old_weights)):
    logger.debug(f"compare first dimensions: {np.all(old_weights[i] == new_weights[i])}")
    for j in range(len(old_weights[i])):
        logger.debug(f"compare second dimensions: {np.all(old_weights[i][j] == new_weights[i][j])}")