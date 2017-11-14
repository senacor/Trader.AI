'''
Created on 13.11.2017

@author: jtymoszuk
'''
import random
from collections import deque
import numpy as np

from predicting.predictor_interface import IPredictor
from predicting.simple_predictor import SimplePredictor
from trading.trader_interface import Portfolio, TradingAction
from trading.trader_interface import ITrader
from trading.trader_interface import StockMarketData
from trading.trader_interface import TradingActionList
from keras.models import Sequential, model_from_json
from keras.layers import Dense
from keras.optimizers import sgd, Adam
from trading.trader_interface import TradingActionEnum
from trading.trader_interface import CompanyEnum
from trading.trader_interface import SharesOfCompany


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

    def input_array(self):
        return np.array([[self.cash, self.stockA, self.stockB, self.priceA, self.priceB, self.predictedA, self.predictedB]])



class RnnTrader(ITrader):
    '''
    Implementation of ITrader based on Reinforced Neural Network (RNN): doTrade generates TradingActionList according to last generated changes on Portfolio value.
    '''

    def __init__(self, stockAPredictor: IPredictor, stockBPredictor: IPredictor):
        '''
        Constructor
        '''
        # Save predictors
        self.stockAPredictor = stockAPredictor
        self.stockBPredictor = stockBPredictor

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

        # create main model, either from file or (if not existent) from scratch
        try:
            self.model = self.load_model()
        except:
            self.model = self.build_model()

        # create and initialize target model
        # self.target_model = self.build_model()
        #self.update_target_model()

        self.lastPortfolioValue = None
        self.lastActionA = None
        self.lastActionB = None

    # TODO description
    def build_model(self) -> Sequential:
        model = Sequential()
        model.add(Dense(self.hidden_size, input_dim=self.state_size, activation='relu', kernel_initializer='he_uniform'))
        model.add(Dense(self.hidden_size, activation='relu', kernel_initializer='he_uniform'))
        # tanh for output between -1 and +1
        model.add(Dense(self.action_size, activation='tanh', kernel_initializer='he_uniform'))
        # model.summary()
        model.compile(loss='mse', optimizer=Adam(lr=self.learning_rate))
        return model

    # TODO description
    def save_model(self):
        model_json = self.model.to_json()
        with open("rnn_trader.json", "w") as json_file:
            json_file.write(model_json)
        self.model.save_weights("rnn_trader.h5")

    # TODO description
    def load_model(self) -> Sequential:
        json_file = open('rnn_trader.json', 'r')
        loaded_model_json = json_file.read()
        json_file.close()
        model = model_from_json(loaded_model_json)
        model.load_weights('rnn_trader.h5')
        return model

    # Get best action for current state, either randomly or predicted from neural network
    # Choice between random and neural network solely depends on epsilon
    # Epsilon is the probability of a random action
    # Return value is two floats between -1.0 and +1.0
    # First float is for action on stock A, second float is for action on stock B
    # Minus means "sell stock proportionally to owned amount", e.g. -0.5 means "sell half of your owned stock"
    # Plus means "buy stock proportionally to owned cash", e.g. +0.5 means "take half of your cash and by that stock"
    def get_action(self, state: State):
        if np.random.rand() <= self.epsilon:
            # generate two random floats, each between -1 and +1
            return random.uniform(-1.0, 1.0), random.uniform(-1.0, 1.0)
        else:
            # call neural network with current state
            actions = self.model.predict(state.input_array())
            return actions[0][0], actions[0][1]

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

    # TODO why company names as parameters? we don't use them
    def doTrade(self, portfolio: Portfolio, currentPortfolioValue: float, stockMarketData: StockMarketData,
                company_a_name=CompanyEnum.COMPANY_A.value,
                company_b_name=CompanyEnum.COMPANY_B.value) -> TradingActionList:
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
       
        # build current state object
        current_state = None
        if self.lastPortfolioValue is not None: # doTrade was called before at least once
            assert self.lastActionA is not None and self.lastActionB is not None
            # baue memory tuple auf
            # memory tuple speichern
            # nehmen zufällige Teilmenge von memory
            # trainieren model mit obiger Teilmenge

        # Create actions for current state and save them for the next call of doTrade
        self.lastActionA, self.lastActionB = self.get_action(current_state)
        self.lastPortfolioValue = currentPortfolioValue
        return self.create_TradingActionList(self.lastActionA, self.lastActionB, portfolio)

    def create_TradingActionList(self, actionA: float, actionB: float, currentPortfolio: Portfolio) -> TradingActionList:
        """
        Creates TradingActionList for later Evaluation
        Args:
          actionA : float value between -1.0 and 1.0, representing operation (Buy=positive or Sell=negative) and percentage of shares to consider for Company A
          actionB : float value between -1.0 and 1.0, representing operation (Buy=positive or Sell=negative) and percentage of shares to consider for Company B
          currentPortfolio : current Portfolio of this Trader
        Returns:
          A TradingActionList instance, may be empty never None
        """
        result = TradingActionList()
        
        tradingActionA = self.create_TradingAction(CompanyEnum.COMPANY_A, actionA, currentPortfolio)
        if(tradingActionA is not None):
            result.addTradingAction(tradingActionA)
            
        tradingActionB = self.create_TradingAction(CompanyEnum.COMPANY_B, actionB, currentPortfolio)        
        if(tradingActionB is not None):
            result.addTradingAction(tradingActionB)  
        
        return result

    def create_TradingAction(self, companyEnum: CompanyEnum, action: float, currentPortfolio: Portfolio) -> TradingAction:
        """
        Creates single TradingAction for later evaluation in Stock Market
        Args:
          companyEnum : CompanyEnum describes current Company
          action : float value between -1.0 and 1.0, representing operation (Buy=positive or Sell=negative) and percentage of shares to consider for given Company
          currentPortfolio : current Portfolio of this Trader
        Returns:
          A TradingAction instance, may be None
        """
        assert action >= -1.0 and action <= 1.0
        
        tradingAction = None
        if (action > 0.0):
            tradingAction = TradingActionEnum.BUY
        elif (action < 0.0):
            tradingAction = TradingActionEnum.SELL
        
        if (tradingAction is not None):
            sharesOfCompany = currentPortfolio.get_by_name(companyEnum.value)
            if(sharesOfCompany is not None):
                # Percent of actions to sell/buy multiply by number of owned actions
                amountOfSharesOfComapanyToSellOrBuy = abs(int(action * sharesOfCompany.amount))
                
                sharesOfCompanyToSellOrBuy = SharesOfCompany(companyEnum, amountOfSharesOfComapanyToSellOrBuy)
                
                return TradingAction(tradingAction, sharesOfCompanyToSellOrBuy)
            else:
                # TODO: use Logging!!!
                print(f"!!!! RnnTrader - WARNING: sharesOfCompany {companyEnum.value} NOT found in Portfolio {currentPortfolio}")
        else:
            # TODO: use Logging!!!
            print(f"!!!! RnnTrader - INFO: sTrading action is None, action: {action}, Portfolio: {currentPortfolio}")
        
        return None

    def isTradingActionListValid(self, tradingActionList : TradingActionList, currentPortfolio: Portfolio, stockMarketData: StockMarketData) -> bool:
        """
        Validates if generated TradingActionList is valid in comparison to current Portfolio
        Args:
          tradingActionList : TradingActionList containing generated TradingAction's to be sent into Evaluation (Stock Market)
          currentPortfolio : current Portfolio of this Trader
          stockMarketData: StockMarketData containing date for all companies 
        Returns:
          A True if given TradingActionList is valid in comparison to current Portfolio, False otherwise, never None
        """
        
        currentCash = currentPortfolio.cash

        mostRecentPriceCompanyA = stockMarketData.get_most_recent_price(CompanyEnum.COMPANY_A.value)
        tradingActionForCompanyA = tradingActionList.get_by_CompanyEnum(CompanyEnum.COMPANY_A)
        
        isValid, currentCash = self.isTradingActionValid(currentCash, CompanyEnum.COMPANY_A.value, tradingActionForCompanyA, mostRecentPriceCompanyA, currentPortfolio)
        if(isValid is False):
            return False
        
        mostRecentPriceCompanyB = stockMarketData.get_most_recent_price(CompanyEnum.COMPANY_A.value)
        tradingActionForCompanyB = tradingActionList.get_by_CompanyEnum(CompanyEnum.COMPANY_B)
        
        isValid, currentCash = self.isTradingActionValid(currentCash, CompanyEnum.COMPANY_B.value, tradingActionForCompanyB, mostRecentPriceCompanyB, currentPortfolio)
        if(isValid is False):
            return False
        
        return True

    def isTradingActionValid(self, currentCash: float, companyName: str, tradingActionForCompany: TradingAction, mostRecentPriceCompany: float, currentPortfolio: Portfolio):
        """
        Validates if given TradingAction is valid
        Args:
          currentCash : TradingActionList containing generated TradingAction's to be sent into Evaluation (Stock Market)
          companyName : Company name as String
          tradingActionForCompany: TradingAction
          mostRecentPriceCompany: most recent price of company as float 
          currentPortfolio: current Portfolio
        Returns:
          A True if given TradingAction is valid in comparison to current Portfolio and Cash, False otherwise, never None
        """
        if(tradingActionForCompany is not None):
            if(tradingActionForCompany.action == TradingActionEnum.BUY):
                priceToPay = mostRecentPriceCompany * tradingActionForCompany.shares
                
                currentCash = currentCash - priceToPay
                if(currentCash < 0):
                    # TODO: use Logging!!!
                    print(f"!!!! RnnTrader - WARNING: Not enough money to pay! tradingActionForCompany: {tradingActionForCompany}, Portfolio: {currentPortfolio}")
                    return False, currentCash
                
            elif (tradingActionForCompany.action == TradingActionEnum.SELL):
                if (tradingActionForCompany.shares > currentPortfolio.get_by_name(companyName).amount):
                    return False
            else:
                raise ValueError(f'Action for tradingActionForCompanyB is not valid: {tradingActionForCompany}') 
            
        return True, currentCash

    # TODO remove?
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
from evaluating.portfolio_evaluator import PortfolioEvaluator
from evaluating.evaluator import read_stock_market_data
EPISODES = 2
if __name__ == "__main__":
    # Reading training data
    training_data = read_stock_market_data(['stock_a_1962-2011', 'stock_b_1962-2011'])

    # Define initial portfolio
    initial_portfolio = Portfolio(50000.0, [], 'RNN trader portfolio')

    # Define this trader, thereby loading trained networks
    trader = RnnTrader(SimplePredictor(), SimplePredictor())

    # Start evaluation and thereby learn training data
    evaluator = PortfolioEvaluator([trader], False)
    for i in range(EPISODES):
        evaluator.inspect_over_time(training_data, [initial_portfolio])

    # Save trained neural network
    trader.save_net()
