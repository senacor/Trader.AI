'''
Created on 19.11.2017

@author: rmueller
'''
import random
from collections import deque
import numpy as np

from evaluating.portfolio_evaluator import PortfolioEvaluator
from model.StockData import StockData
from model.Portfolio import Portfolio
from model.StockMarketData import StockMarketData
from model.IPredictor import IPredictor
from predicting.predictor.perfect_predictor import PerfectPredictor
from predicting.predictor.random_predictor import RandomPredictor
from model.ITrader import ITrader
from model.trader_actions import TradingActionList, TradingAction
from keras.models import Sequential
from keras.layers import Dense
from keras.optimizers import Adam
from model.trader_actions import TradingActionEnum
from model.trader_actions import CompanyEnum
from model.trader_actions import SharesOfCompany

from utils import save_keras_sequential, load_keras_sequential, read_stock_market_data
from logger import logger

# Define possible actions per stock
STOCKACTIONS = [+1.0, +0.5, 0.0, -0.5, -1.0]


class State:
    """
    Represents state from the trader's viewpoint
    """
    def __init__(self, cash: float, stockA: int, stockB: int, priceA: float, priceB: float, predictedA: float,
                 predictedB: float):
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

    def get_input_array(self):
        return np.array(
            [[self.cash, self.stockA, self.stockB, self.priceA, self.priceB, self.predictedA, self.predictedB]])



class DqlTrader(ITrader):
    """
    Implementation of ITrader based on reinforced Q-learning (RQL).
    """
    def __init__(self, stock_a_predictor: IPredictor, stock_b_predictor: IPredictor, use_trained_model: bool = True):
        """
        TODO
        Args:
            stock_a_predictor:
            stock_b_predictor:
            use_trained_model:
        """
        # Save predictors
        self.stock_a_predictor = stock_a_predictor
        self.stock_b_predictor = stock_b_predictor

        # Hyper parameters for neural network
        self.state_size = 7
        self.action_size = len(STOCKACTIONS) * len(STOCKACTIONS)
        self.hidden_size = 50

        # Hyper parameters for deep Q-learning
        self.learning_rate = 0.001
        self.epsilon = 1.0
        self.epsilon_decay = 0.999
        self.epsilon_min = 0.01
        self.batch_size = 64

        # Parameters for experience memory
        self.memory = deque(maxlen=2000)
        self.train_start = 100
        self.lastPortfolioValue = None
        self.lastActionA = None
        self.lastActionB = None
        self.lastState = None

        # Create main model, either as trained model (from file) or as untrained model (from scratch)
        self.model = None
        if use_trained_model:
            self.model = load_keras_sequential('trading', 'dql_trader')
            logger.info(f"DQL Trader: Loaded trained model!")
        if self.model is None: # loading failed or we didn't want to use a trained model
            self.model = Sequential()
            self.model.add(Dense(self.hidden_size, input_dim=self.state_size, activation='relu', kernel_initializer='he_uniform'))
            self.model.add(Dense(self.hidden_size, activation='relu', kernel_initializer='he_uniform'))
            self.model.add(Dense(self.action_size, activation='relu', kernel_initializer='he_uniform'))
            logger.info(f"DQL Trader: Create new untrained model!")
        assert self.model is not None
        self.model.compile(loss='mse', optimizer=Adam(lr=self.learning_rate))

    def save_trained_model(self):
        """
        Save the trained neural network under a fixed name specific for this trader.
        """
        print(f"DQL Trader: Saving trained model")
        save_keras_sequential(self.model, 'trading', 'dql_trader')

    def get_action(self, state: State):
        """
        Get best action for current state, either randomly or predicted from neural network
        Choice between random and neural network solely depends on epsilon
        Epsilon is the probability of a random action
        Return value is two floats between -1.0 and +1.0
        First float is for action on stock A, second float is for action on stock B
        Minus means "sell stock proportionally to owned amount", e.g. -0.5 means "sell half of your owned stock"
        Plus means "buy stock proportionally to owned cash", e.g. +0.5 means "take half of your cash and by that stock"
        ATTENTION: if sum of action over all stocks is greater than 1.0, then not all stocks can be bought!
        Example: action stock A = +1.0 and action stock B = +0.2
        This leads to all cash to be spent on buying stock A (because of action +1.0),
        which in turn means there is no cash left to buy stock B (the action +0.2)
        """
        if np.random.rand() <= self.epsilon:
            # Generate and return two random actions
            return random.choice(STOCKACTIONS), random.choice(STOCKACTIONS)
        else:
            # Generate values per action by calling neural network with current state
            action_values = self.model.predict(state.get_input_array())
            # Get index with highest value (if there are more than one, get the first), and return corresponding actions
            index = np.argmax(action_values[0])
            return self.get_actions_from_index(index)

    def get_actions_from_index(self, index: int):
        """
        Convert index from neural network output into two STOCKACTIONS.
        Args:
            index: Index of corrsponding combination of STOCKACTIONs in neural network output.

        Returns:
            Two STOCKACTIONs, one for stock A and one for stock B.
        """
        assert 0 <= index < self.action_size
        return STOCKACTIONS[index // len(STOCKACTIONS)], STOCKACTIONS[index % len(STOCKACTIONS)]

    def get_index_from_actions(self, actionA: float, actionB: float):
        """
        Convert two STOCKACTIONS into index of neural network output.
        Args:
            actionA: STOCKACTION for stock A.
            actionB: STOCKACTION for stock B.

        Returns:
            Index of corresponding combination of STOCKACTIONs in neural network output.
        """
        assert actionA in STOCKACTIONS
        assert actionB in STOCKACTIONS
        return STOCKACTIONS.index(actionA) * len(STOCKACTIONS) + STOCKACTIONS.index(actionB)

    def calculate_reward(self, last_portfolio_value: float, current_portfolio_value: float) -> int:
        """
        Implements rewards function
        
        Args:
            last_portfolio_value - last value of Portfolio
            current_portfolio_value - current value of Portfolio
        """
        assert last_portfolio_value is not None
        assert current_portfolio_value is not None

        if current_portfolio_value > last_portfolio_value:
            return 10
        elif current_portfolio_value < last_portfolio_value:
            return -10
        else:
            return 0

    def train_model(self):
        """
        Train the neural network using a small random batch of the stored experiences in memory.
        """
        # Only train if we've seen at least a certain amount of experiences
        if len(self.memory) < self.train_start:
            return
        batch_size = min(self.batch_size, len(self.memory))
        batch = random.sample(self.memory, batch_size)

        for state, actionA, actionB, reward, nextState in batch:
            # We ignore future rewards and focus solely on short-term trading
            target = reward

            # Build target action values and exchange value for the chosen actions
            target_action_values = self.model.predict(state.get_input_array())
            index = self.get_index_from_actions(actionA, actionB)
            target_action_values[0][index] = target

            # Finally train the model for one epoch
            self.model.fit(state.get_input_array(), target_action_values, batch_size=self.batch_size, epochs=1, verbose=1)

    def doTrade(self, portfolio: Portfolio, current_portfolio_value: float,
                stock_market_data: StockMarketData) -> TradingActionList:
        """ Generate action to be taken on the "stock market"
    
        Args:
          portfolio : current Portfolio of this trader
          current_portfolio_value : value of Portfolio at given Momemnt
          stock_market_data : StockMarketData for evaluation
        Returns:
          A TradingActionList instance, may be empty never None
        """
        # build current state object
        stock_a_data = stock_market_data.get_for_company(CompanyEnum.COMPANY_A)
        stock_b_data = stock_market_data.get_for_company(CompanyEnum.COMPANY_B)
        predicted_stock_a = self.stock_a_predictor.doPredict(stock_a_data)
        predicted_stock_b = self.stock_b_predictor.doPredict(stock_b_data)
        current_state = State(portfolio.cash,
                              portfolio.get_amount(CompanyEnum.COMPANY_A),
                              portfolio.get_amount(CompanyEnum.COMPANY_B),
                              stock_market_data.get_most_recent_price(CompanyEnum.COMPANY_A),
                              stock_market_data.get_most_recent_price(CompanyEnum.COMPANY_B),
                              predicted_stock_a,
                              predicted_stock_b)

        if self.lastState is not None:  # doTrade was called before at least once
            assert self.lastActionA is not None and self.lastActionB is not None and self.lastPortfolioValue is not None
            # Calculate reward and store state, actions, reward and following state in memory
            reward = self.calculate_reward(self.lastPortfolioValue, current_portfolio_value)
            memoryTuple = (self.lastState, self.lastActionA, self.lastActionB, reward, current_state)
            self.memory.append(memoryTuple)
            # Train from experiences stored in memory
            self.train_model()

        # Create actions for current state
        action_a, action_b = self.get_action(current_state)
        logger.info(f"DQL Trader: Computed trading actions {action_a} and {action_b}")
        # Decrease epsilon for fewer random actions
        self.epsilon = max([self.epsilon_min, self.epsilon * self.epsilon_decay])
        # Save created actions for the next call of doTrade
        self.lastActionA = action_a
        self.lastActionB = action_b
        self.lastPortfolioValue = current_portfolio_value
        self.lastState = current_state
        return self.create_trading_actions(action_a, action_b, portfolio, stock_market_data)

    def create_trading_actions(self, action_a: float, action_b: float, portfolio: Portfolio, stock_market_data: StockMarketData) -> TradingActionList:
        """
        Take output from neural net (two floats from STOCKACTIONS) and convert it into corresponding trading actions.
        Args:
            action_a: float between -1.0 and 1.0, representing buy(positive)/sell(negative) and percentage of shares to consider for Company A
            action_b: float between -1.0 and 1.0, representing buy(positive)/sell(negative) and percentage of shares to consider for Company B
            portfolio: current portfolio of this trader
            stock_market_data: current stock market data

        Returns:
            List of corresponding TradingActions
        """
        assert action_a in STOCKACTIONS and action_b in STOCKACTIONS
        assert portfolio is not None and stock_market_data is not None
        trading_actions = TradingActionList()

        # Create trading actions for stock A
        owned_amount = portfolio.get_amount(CompanyEnum.COMPANY_A)
        if action_a < 0.0 and owned_amount > 0:
            amount_to_sell = int(abs(action_a) * owned_amount)
            trading_actions.sell(CompanyEnum.COMPANY_A, amount_to_sell)
        if action_a > 0.0:
            current_price = stock_market_data.get_most_recent_price(CompanyEnum.COMPANY_A)
            amount_to_buy = int(action_a * (portfolio.cash // current_price))
            trading_actions.buy(CompanyEnum.COMPANY_A, amount_to_buy)
        # Create trading actions for stock B
        owned_amount = portfolio.get_amount(CompanyEnum.COMPANY_B)
        if action_b < 0.0 and owned_amount > 0:
            amount_to_sell = int(abs(action_b) * owned_amount)
            trading_actions.sell(CompanyEnum.COMPANY_B, amount_to_sell)
        if action_b > 0.0:
            current_price = stock_market_data.get_most_recent_price(CompanyEnum.COMPANY_B)
            amount_to_buy = int(action_b * (portfolio.cash // current_price))
            trading_actions.buy(CompanyEnum.COMPANY_B, amount_to_buy)
        return trading_actions



# This method retrains the trader from scratch using training data from 1962-2011
EPISODES = 1
if __name__ == "__main__":
    # Reading training data
    training_data = read_stock_market_data([CompanyEnum.COMPANY_A, CompanyEnum.COMPANY_B], ['2012-2017'])

    # Define initial portfolio
    portfolio = Portfolio(10000.0, [], 'DQL trader portfolio')

    # Initialize trader: use perfect predictors, don't use an already trained model, but learn while trading
    #trader = DqlTrader(PerfectPredictor(CompanyEnum.COMPANY_A), PerfectPredictor(CompanyEnum.COMPANY_B), False)
    trader = DqlTrader(PerfectPredictor(CompanyEnum.COMPANY_A), PerfectPredictor(CompanyEnum.COMPANY_B), True)

    # Start evaluation and train correspondingly; display the results in a plot
    evaluator = PortfolioEvaluator([trader], True)
    for i in range(EPISODES):
        evaluator.inspect_over_time(training_data, [portfolio])
    trader.save_trained_model()
