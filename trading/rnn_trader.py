'''
Created on 13.11.2017

@author: jtymoszuk
'''
import random
from collections import deque

import numpy as np
from trading.trader_interface import Portfolio
from trading.trader_interface import ITrader
from trading.trader_interface import StockMarketData
from trading.trader_interface import TradingActionList
from keras.models import Sequential
from keras.layers import Dense
from keras.optimizers import sgd, Adam


# Define state from the trader's viewpoint
class State:
    def __init__(self, cash: float, stockA: int, stockB: int, priceA: float, priceB: float, predictedA: float, predictedB: float):
        self.cash = cash
        self.stockA = stockA
        self.stockB = stockB
        self.priceA = priceA
        self.priceB = priceB
        self.predictedA = predictedA
        self.predictedB = predictedB

    def print(self):
        print(f"cash: {self.cash}, "
              f"A: {self.stockA} x {self.priceA} ({self.predictedA}), "
              f"B: {self.stockB} x {self.priceB} ({self.predictedB})")

    def deepcopy(self):
        return State(self.cash, self.stockA, self.stockB, self.priceA, self.priceB, self.predictedA, self.predictedB)

    def array(self):
        return np.array([self.cash, self.stockA, self.stockB, self.priceA, self.priceB, self.predictedA, self.predictedB])



class RnnTrader(ITrader):
    '''
    Implementation of ITrader based on Reinforced Neural Network (RNN): doTrade generates TradingActionList according to last generated changes on Portfolio value.
    '''

    def __init__(self):
        '''
        Constructor
        '''
        # Hyperparameters for neural network
        self.state_size = 7 # TODO: infer from...
        self.action_size = 2 # TODO: infer from ...
        self.hidden_size = 24

        # These are hyper parameters for the DQN
        self.discount_factor = 0.99
        self.learning_rate = 0.001
        self.epsilon = 1.0
        self.epsilon_decay = 0.999
        self.epsilon_min = 0.01
        self.batch_size = 64
        self.train_start = 1000
        # create replay memory using deque
        self.memory = deque(maxlen=2000)

        # create main model and target model
        # TODO create OR load trained model
        #self.model = self.build_model()
        self.model = Sequential()
        self.model.add(Dense(self.hidden_size, input_dim=self.state_size, activation='relu', kernel_initializer='he_uniform'))
        self.model.add(Dense(self.hidden_size, activation='relu', kernel_initializer='he_uniform'))
        self.model.add(Dense(self.action_size, activation='linear', kernel_initializer='he_uniform'))
        #model.summary()
        self.model.compile(loss='mse', optimizer=Adam(lr=self.learning_rate))
        #self.target_model = self.build_model()

        # initialize target model
        #self.update_target_model()

        self.lastPortfolioValue = None
        self.lastActionA = None
        self.lastActionB = None

    # TODO save trained net
    def save_net(self):
        pass

    # TODO get action from model using epsilon-greedy policy
    def get_action(self, state: State):
        if np.random.rand() <= self.epsilon:
            return random.uniform(-1.0, 1.0), random.uniform(-1.0, 1.0)  # two random floats, each between -1 and 1
        else:  # TODO get actions from net
            input = np.array(state[1:])  # cut out date information, it's no input for the net
            # state = np.reshape(state, [1, state_size])
            input = np.reshape(input, [1, self.state_size])
            q_values = self.model.predict(input)
            return np.argmax(q_values[0]), np.argmax(q_values[1])

    # TODO save sample <s,a,r,s'> to the replay memory
    def append_sample(self, state: State, actionA: float, actionB: float, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

    # TODO pick samples randomly from replay memory (with batch_size)
    def train_model(self):
        if len(self.memory) < self.train_start:
            return
        batch_size = min(self.batch_size, len(self.memory))
        mini_batch = random.sample(self.memory, batch_size)

        update_input = np.zeros((batch_size, self.state_size))
        update_target = np.zeros((batch_size, self.state_size))
        action, reward, done = [], [], []

        for i in range(self.batch_size):
            update_input[i] = mini_batch[i][0]
            action.append(mini_batch[i][1])
            reward.append(mini_batch[i][2])
            update_target[i] = mini_batch[i][3]
            done.append(mini_batch[i][4])

        target = self.model.predict(update_input)
        target_val = self.target_model.predict(update_target)

        for i in range(self.batch_size):
            # Q Learning: get maximum Q value at s' from target model
            if done[i]:
                target[i][action[i]] = reward[i]
            else:
                target[i][action[i]] = reward[i] + self.discount_factor * (
                    np.amax(target_val[i]))

        # and do the model fit!
        self.model.fit(update_input, target, batch_size=self.batch_size,
                       epochs=1, verbose=0)

    def doTrade(self, portfolio: Portfolio, currentPortfolioValue: float, stockMarketData: StockMarketData) -> TradingActionList:
        """ Generate action to be taken on the "stock market"
    
        Args:
          portfolio : current Portfolio of this trader
          currentPortfolioValue : value of Portfolio at given Momemnt
          stockMarketData : StockMarketData for evaluation
          company_a_name : optional name of 1st company, or default
          company_b_name : optional name of 2nd company, or default
        Returns:
          A TradingActionList instance, may be empty never None
        """
        # TODO implement me
        rewardFromLastTrading = self.calculateReward(self.lastPortfolioValue, currentPortfolioValue)
        
        
        
        
        self.lastPortfolioValue = currentPortfolioValue
        return None   
        
    def calculateReward(self, lastPortfolioValue: float, currentPortfolioValue: float) -> int:
        
        if lastPortfolioValue is None or currentPortfolioValue is None:
            return 0
        
        if(currentPortfolioValue > lastPortfolioValue):
            return 1
        elif(currentPortfolioValue < lastPortfolioValue):
            return -1
        else:
            return 0   





# Train the trader and its respective neural network(s)
EPISODES = 1
if __name__ == "__main__":
    # TODO börse initialisieren mit diesem Trader
    # TODO börse starten und dabei lernen lassen
    # TODO trainiertes Netz vom Trader speichern