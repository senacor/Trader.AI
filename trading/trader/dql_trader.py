'''
Created on 19.11.2017

@author: rmueller
'''
import random
from collections import deque
import numpy as np

from evaluating.portfolio_evaluator import PortfolioEvaluator
from model.Portfolio import Portfolio
from model.StockMarketData import StockMarketData
from model.IPredictor import IPredictor
from model.ITrader import ITrader
from model.trader_actions import TradingActionList
from keras.models import Sequential
from keras.layers import Dense
from keras.optimizers import Adam
from model.trader_actions import CompanyEnum

from utils import save_keras_sequential, load_keras_sequential, read_stock_market_data
from logger import logger
from predicting.predictor.reference.perfect_predictor import PerfectPredictor

class State:
    """
    Represents a state from the trader's viewpoint.
    """
    def __init__(self, cash: float, stock_a: int, stock_b: int, price_a: float, price_b: float, predicted_a: float,
                 predicted_b: float):
        """
        Constructor: Creates the state.
        Args:
            cash: Current amount of cash
            stock_a: Current amount of owned stock A
            stock_b: Current amount of owned stock B
            price_a: Current price of stock A
            price_b: Current price of stock B
            predicted_a: Predicted price of stock A
            predicted_b: Predicted price of stock B
        """
        self.cash = cash
        self.stock_a = stock_a
        self.stock_b = stock_b
        self.price_a = price_a
        self.price_b = price_b
        self.predicted_a = predicted_a
        self.predicted_b = predicted_b

    def __repr__(self) -> str:
        """
        Outputs readable representation of this state.
        Returns:
            Readable representation as string
        """
        return f"Cash: {self.cash}, A: {self.stock_a} x {self.price_a} ({self.predicted_a})," \
               f" B: {self.stock_b} x {self.price_b} ({self.predicted_b})"

    def to_model_input(self):
        """
        Converts this state to an input for the DQL trader neural network.
        ATTENTION: If you change this, then you also have to change the value of 'self.state_size' in DqlTrader!
        Returns:
            The State as input vector for the trader's neural network
        """
        # We only input price movements to a DqlTrader
        movement_up_stock_a = self.predicted_a >= self.price_a
        movement_up_stock_b = self.predicted_b >= self.price_b
        return np.array([[movement_up_stock_a, movement_up_stock_b]])



class DqlTrader(ITrader):
    """
    Implementation of ITrader based on reinforced Q-learning (RQL).
    """

    # Stockactions model the possible output from the neural network.
    # A stockaction is of a pair of floats, each between -1.0 and +1.0.
    # The first float encodes an action for stock A, the second float encodes an action for stock B.
    # A float between 0.0 and +1.0 encodes buying a stock, measured in percent of cash of the current portfolio.
    # A float between -1.0 and 0.0 encodes selling a stock, measured in percent of the amount this stock is present
    # in the current portfolio.
    # A float of 0.0 encodes "do nothing", so: no trading action at all.
    # ATTENTION: These stockactions greatly reduce the action space of the neural network and directly influence
    # its training performance. So choose wisely ;-)
    STOCKACTIONS = [(+1.0, +0.0), (+0.0, +1.0),
                    (+0.9, +0.1), (+0.1, +0.9),
                    (+0.8, +0.2), (+0.2, +0.8),
                    (+0.7, +0.3), (+0.3, +0.7),
                    (+0.6, +0.4), (+0.4, +0.6),
                    (+0.5, +0.5),
                    (+1.0, -1.0), (-1.0, +1.0),
                    (-1.0, -1.0)]

    def __init__(self, stock_a_predictor: IPredictor, stock_b_predictor: IPredictor, load_trained_model: bool = True, train_while_trading: bool = False):
        """
        Constructor
        Args:
            stock_a_predictor: Predictor for stock A
            stock_b_predictor: Predictor for stock B
            load_trained_model: Flag to trigger loading an already trained neural network
            train_while_trading: Flag to trigger on-the-fly training while trading
        """
        # Save predictors and training mode
        assert stock_a_predictor is not None and stock_b_predictor is not None
        self.stock_a_predictor = stock_a_predictor
        self.stock_b_predictor = stock_b_predictor
        self.train_while_trading = train_while_trading

        # Hyper parameters for neural network
        self.state_size = 2
        self.action_size = len(self.STOCKACTIONS)
        self.hidden_size = 50

        # Hyper parameters for deep Q-learning
        self.learning_rate = 0.001
        self.epsilon = 1.0
        self.epsilon_decay = 0.999
        self.epsilon_min = 0.01
        self.batch_size = 64
        self.min_size_of_memory = 1000 # should be way bigger than batch_size, but smaller
        self.memory = deque(maxlen=2000)

        # Parameters for experience memory
        # TODO do we need this?
        self.lastPortfolioValue = None
        self.lastActionA = None
        self.lastActionB = None
        self.lastState = None

        # Create main model, either as trained model (from file) or as untrained model (from scratch)
        self.model = None
        if load_trained_model:
            self.model = load_keras_sequential('trading', 'dql_trader')
            logger.info(f"DQL Trader: Loaded trained model!")
        if self.model is None: # loading failed or we didn't want to use a trained model
            self.model = Sequential()
            self.model.add(Dense(self.hidden_size * 2, input_dim=self.state_size, activation='relu'))
            self.model.add(Dense(self.hidden_size, activation='relu'))
            self.model.add(Dense(self.action_size, activation='linear'))
            logger.info(f"DQL Trader: Created new untrained model!")
        assert self.model is not None
        self.model.compile(loss='mse', optimizer=Adam(lr=self.learning_rate))

    def save_trained_model(self):
        """
        Save the trained neural network under a fixed name specific for this trader.
        """
        save_keras_sequential(self.model, 'trading', 'dql_trader')
        logger.info(f"DQL Trader: Saved trained model")

    def get_action(self, state: State) -> (float, float):
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
        if self.train_while_trading and np.random.rand() <= self.epsilon:
            # Generate and return two random actions
            logger.debug(f"DQL Trader: Choose random actions")
            return random.choice(self.STOCKACTIONS)
        else:
            # Generate values per action by calling neural network with current state
            action_values = self.model.predict(state.to_model_input())
            logger.debug(f"DQL Trader: Use trained model to choose from {action_values}")
            # Get index with highest value (if there are more than one, get the first), and return corresponding actions
            index = np.argmax(action_values[0])
            logger.debug(f"DQL Trader: Choosen index: {index}")
            return self.STOCKACTIONS[index]

    def get_actions_from_index(self, index: int):
        """
        Convert index from neural network output into two STOCKACTIONS.
        Args:
            index: Index of corrsponding combination of STOCKACTIONs in neural network output.

        Returns:
            Two STOCKACTIONs, one for stock A and one for stock B.
        """
        assert 0 <= index < self.action_size
        #return STOCKACTIONS[index // len(STOCKACTIONS)], STOCKACTIONS[index % len(STOCKACTIONS)]

    def get_index_from_actions(self, actionA: float, actionB: float):
        """
        Convert two STOCKACTIONS into index of neural network output.
        Args:
            actionA: STOCKACTION for stock A.
            actionB: STOCKACTION for stock B.

        Returns:
            Index of corresponding combination of STOCKACTIONs in neural network output.
        """
        # assert actionA in STOCKACTIONS
        # assert actionB in STOCKACTIONS
        # return STOCKACTIONS.index(actionA) * len(STOCKACTIONS) + STOCKACTIONS.index(actionB)

    def calculate_reward(self, current_state: State, last_portfolio_value: float, current_portfolio_value: float) -> float:
        """
        Implements rewards function
        
        Args:
            last_portfolio_value - last value of Portfolio
            current_portfolio_value - current value of Portfolio
        """
        assert current_state is not None
        assert last_portfolio_value is not None and current_portfolio_value is not None

        # Compare performance without action to performance with the taken actions
        # old_portfolio_at_todays_prices = self.lastState.cash + (self.lastState.stockA *  current_state.priceA) + (self.lastState.stockB * current_state.priceB)
        # logger.debug(f"DQL Trader: Old value {old_portfolio_at_todays_prices} and todays value {current_portfolio_value}")
        # if current_portfolio_value >= old_portfolio_at_todays_prices:
        #     return +100
        # else:
        #     return -100


        # Explicitly model logik of SimpleTrader
        # if self.lastState.predictedA - self.lastState.priceA > 0:
        #     if self.lastState.predictedB - self.lastState.priceB > 0: # A up, B up
        #         if self.lastActionA > 0 and self.lastActionB > 0:
        #             return 100
        #         else:
        #             return -100
        #     else: # A up, B down
        #         if self.lastActionA > 0 and self.lastActionB < 0:
        #             return 100
        #         else:
        #             return -100
        # else:
        #     if self.lastState.predictedB - self.lastState.priceB > 0: # A down, B up
        #         if self.lastActionA < 0 and self.lastActionB > 0:
        #             return 100
        #         else:
        #             return -100
        #     else: # A down, B down
        #         if self.lastActionA < 0 and self.lastActionB < 0:
        #             return 100
        #         else:
        #             return -100

        # Only check portfolio value
        # if current_portfolio_value > last_portfolio_value:
        #     return +100
        # elif current_portfolio_value == last_portfolio_value:
        #     return 0
        # else:
        #     return -100
        if current_portfolio_value > last_portfolio_value:
            return ((current_portfolio_value / last_portfolio_value) * 10.0) * ((current_portfolio_value / last_portfolio_value) * 10.0)
        elif current_portfolio_value == last_portfolio_value:
            return 0.0
        else:
            return -100.0

    def train_model(self):
        """
        Train the neural network using a small random batch of the stored experiences in memory.
        """
        # Only train if we've seen at least a certain amount of experiences
        # if len(self.memory) < self.train_start:
        #     return
        # batch_size = min(self.batch_size, len(self.memory))
        # batch = random.sample(self.memory, batch_size)
        assert len(self.memory) >= self.batch_size
        batch = random.sample(self.memory, self.batch_size)

        for state, actionA, actionB, reward, nextState in batch:
            # We ignore future rewards and focus solely on short-term trading
            target = reward

            # Build target action values and exchange value for the chosen actions
            output_values = self.model.predict(state.to_model_input())
            #index = self.get_index_from_actions(actionA, actionB)
            index = self.STOCKACTIONS.index((actionA, actionB))
            logger.debug(f"DQL Trader: actionA: {actionA}, actionB: {actionB}, index of action to target: {index}, reward: {target}")
            target_action_values = self.model.predict(state.to_model_input())
            target_action_values[0][index] = target
            logger.debug(
                f"DQL Trader: Before training: Input {state.to_model_input()} Output {output_values} Expected {target_action_values}")

            # Finally train the model for one epoch
            self.model.fit(state.to_model_input(), target_action_values, batch_size=self.batch_size, epochs=1, verbose=0)
            output_values = self.model.predict(state.to_model_input())
            logger.debug(
                f"DQL Trader: After training: Input {state.to_model_input()} Output {output_values} Expected {target_action_values}")

    def doTrade(self, portfolio: Portfolio, current_portfolio_value: float,
                stock_market_data: StockMarketData) -> TradingActionList:
        """ Generate action to be taken on the "stock market"
    
        Args:
          portfolio : current Portfolio of this trader
          current_portfolio_value : value of Portfolio at given moment
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
        logger.debug(f"DQL Trader: Current state: {current_state}")

        if self.train_while_trading and self.lastState is not None:  # doTrade was called before at least once
            assert self.lastActionA is not None and self.lastActionB is not None and self.lastPortfolioValue is not None
            # Calculate reward and store state, actions, reward and following state in memory
            reward = self.calculate_reward(current_state, self.lastPortfolioValue, current_portfolio_value)
            memory_tuple = (self.lastState, self.lastActionA, self.lastActionB, reward, current_state)
            self.memory.append(memory_tuple)
            # Train from experiences stored in memory (once we have enough experiences)
            if len(self.memory) > self.batch_size + self.min_size_of_memory:
                self.train_model()

        # Create actions for current state
        (action_a, action_b) = self.get_action(current_state)
        logger.debug(f"DQL Trader: Computed trading actions {action_a} and {action_b}")
        # Decrease epsilon for fewer random actions
        self.epsilon = max([self.epsilon_min, self.epsilon * self.epsilon_decay])
        # Save created actions for the next call of doTrade
        self.lastActionA = action_a
        self.lastActionB = action_b
        self.lastPortfolioValue = current_portfolio_value
        self.lastState = current_state
        return self.create_trading_actions(action_a, action_b, portfolio, stock_market_data)

    def create_trading_actions(self, action_a: float, action_b: float,
                               portfolio: Portfolio, stock_market_data: StockMarketData) -> TradingActionList:
        """
        Take two floats between -1.0 and +1.0 (one for stock A and one for stock B) and convert them into corresponding
        trading actions.
        Args:
            action_a: float between -1.0 and 1.0, representing buy(positive) / sell(negative) for Company A
            action_b: float between -1.0 and 1.0, representing buy(positive) / sell(negative) for Company B
            portfolio: current portfolio of this trader
            stock_market_data: current stock market data

        Returns:
            List of corresponding TradingActions
        """
        assert -1.0 <= action_a <= +1.0 and -1.0 <= action_b <= +1.0
        assert portfolio is not None and stock_market_data is not None
        trading_actions = TradingActionList()

        # Create trading actions for stock A
        owned_amount_a = portfolio.get_amount(CompanyEnum.COMPANY_A)
        if action_a > 0.0:
            current_price = stock_market_data.get_most_recent_price(CompanyEnum.COMPANY_A)
            amount_to_buy = int(action_a * (portfolio.cash // current_price))
            trading_actions.buy(CompanyEnum.COMPANY_A, amount_to_buy)
        if action_a < 0.0 and owned_amount_a > 0:
            amount_to_sell = int(abs(action_a) * owned_amount_a)
            trading_actions.sell(CompanyEnum.COMPANY_A, amount_to_sell)
        # Create trading actions for stock B
        owned_amount_b = portfolio.get_amount(CompanyEnum.COMPANY_B)
        if action_b > 0.0:
            current_price = stock_market_data.get_most_recent_price(CompanyEnum.COMPANY_B)
            amount_to_buy = int(action_b * (portfolio.cash // current_price))
            trading_actions.buy(CompanyEnum.COMPANY_B, amount_to_buy)
        if action_b < 0.0 and owned_amount_b > 0:
            amount_to_sell = int(abs(action_b) * owned_amount_b)
            trading_actions.sell(CompanyEnum.COMPANY_B, amount_to_sell)
        return trading_actions



# This method retrains the trader from scratch using training data from 1962-2011
EPISODES = 50
if __name__ == "__main__":
    # Reading training data
    #training_data = read_stock_market_data([CompanyEnum.COMPANY_A, CompanyEnum.COMPANY_B], ['1962-2011', '2012-2017'])
    training_data = read_stock_market_data([CompanyEnum.COMPANY_A, CompanyEnum.COMPANY_B], ['2012-2017'])

    # Define initial portfolio
    name = 'DQL trader portfolio'
    portfolio = Portfolio(10000.0, [], name)

    # Initialize trader: use perfect predictors, don't use an already trained model, but learn while trading
    trader = DqlTrader(PerfectPredictor(CompanyEnum.COMPANY_A), PerfectPredictor(CompanyEnum.COMPANY_B), False, True)
    #trader = DqlTrader(PerfectPredictor(CompanyEnum.COMPANY_A), PerfectPredictor(CompanyEnum.COMPANY_B), True, False)

    # Start evaluation and train correspondingly; display the results in a plot
    evaluator = PortfolioEvaluator([trader], False)
    for i in range(EPISODES):
        logger.error(f"DQL Trader: Starting training episode {i}")
        all_portfolios_over_time = evaluator.inspect_over_time(training_data, [portfolio], 300)
        # Get final portfolio value
        trader_portfolio_over_time = all_portfolios_over_time[name]
        import datetime as dt
        final_day = dt.date(2017, 11, 6)
        trader_portfolio = trader_portfolio_over_time[final_day]
        logger.error(f"DQL Trader: Finished training episode {i}, final portfolio value {trader_portfolio.total_value(final_day, training_data)}")
        trader.save_trained_model()
