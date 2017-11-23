"""
Created on 19.11.2017

@author: rmueller
"""
import random
from collections import deque
import numpy as np
import datetime as dt

from definitions import PERIOD_1, PERIOD_2, DQLTRADER_NN_BINARY_PREDICTOR
from evaluating.portfolio_evaluator import PortfolioEvaluator
from model.Portfolio import Portfolio
from model.StockMarketData import StockMarketData
from model.IPredictor import IPredictor
from model.ITrader import ITrader
from model.Order import OrderList
from keras.models import Sequential
from keras.layers import Dense
from keras.optimizers import Adam
from model.Order import CompanyEnum
from utils import save_keras_sequential, load_keras_sequential, read_stock_market_data
from logger import logger
from predicting.predictor.reference.nn_binary_predictor import StockANnBinaryPredictor, StockBNnBinaryPredictor


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

    # Stock actions model the possible output from the neural network.
    # A stock action is of a pair of floats, each between -1.0 and +1.0.
    # The first float encodes an action for stock A, the second float encodes an action for stock B.
    # A float between 0.0 and +1.0 encodes buying a stock, measured in percent of cash of the current portfolio.
    # A float between -1.0 and 0.0 encodes selling a stock, measured in percent of the amount this stock is present
    # in the current portfolio.
    # A float of 0.0 encodes "do nothing", so: no orders at all.
    # ATTENTION: These stock actions vastly reduce the action space of the neural network and directly influence
    # its training performance. So choose wisely ;-)
    STOCK_ACTIONS = [(+1.00, +0.00), (+0.00, +1.00),
                     (+0.95, +0.05), (+0.05, +0.95),
                     (+0.90, +0.10), (+0.10, +0.90),
                     (+0.85, +0.15), (+0.15, +0.85),
                     (+0.80, +0.20), (+0.20, +0.80),
                     (+0.75, +0.25), (+0.25, +0.75),
                     (+0.70, +0.30), (+0.30, +0.70),
                     (+0.65, +0.35), (+0.35, +0.65),
                     (+0.60, +0.40), (+0.40, +0.60),
                     (+0.55, +0.45), (+0.45, +0.55),
                     (+0.50, +0.50),
                     (+1.0, -1.0), (-1.0, +1.0),
                     (-1.0, -1.0)]

    def __init__(self, stock_a_predictor: IPredictor, stock_b_predictor: IPredictor,
                 load_trained_model: bool = True,
                 train_while_trading: bool = False, name: str = 'dql_trader'):
        """
        Constructor
        Args:
            stock_a_predictor: Predictor for stock A
            stock_b_predictor: Predictor for stock B
            load_trained_model: Flag to trigger loading an already trained neural network
            train_while_trading: Flag to trigger on-the-fly training while trading
        """
        # Save predictors, training mode and name
        assert stock_a_predictor is not None and stock_b_predictor is not None
        self.stock_a_predictor = stock_a_predictor
        self.stock_b_predictor = stock_b_predictor
        self.train_while_trading = train_while_trading
        self.name = name

        # Parameters for neural network
        self.state_size = 2
        self.action_size = len(self.STOCK_ACTIONS)
        self.hidden_size = 50

        # Parameters for deep Q-learning
        self.learning_rate = 0.001
        self.epsilon = 1.0
        self.epsilon_decay = 0.999
        self.epsilon_min = 0.01
        self.batch_size = 64
        self.min_size_of_memory_before_training = 1000  # should be way bigger than batch_size, but smaller than memory
        self.memory = deque(maxlen=2000)

        # Attributes necessary to remember our last actions and fill our memory with experiences
        self.last_state = None
        self.last_action_a = None
        self.last_action_b = None
        self.last_portfolio_value = None

        # Create main model, either as trained model (from file) or as untrained model (from scratch)
        self.model = None
        if load_trained_model:
            logger.debug(f"DQL Trader: Try to load trained model")
            self.model = load_keras_sequential('trading', self.name)
            logger.debug(f"DQL Trader: Loaded trained model")
        if self.model is None:  # loading failed or we didn't want to use a trained model
            self.model = Sequential()
            self.model.add(Dense(self.hidden_size * 2, input_dim=self.state_size, activation='relu'))
            self.model.add(Dense(self.hidden_size, activation='relu'))
            self.model.add(Dense(self.action_size, activation='linear'))
            logger.info(f"DQL Trader: Created new untrained model")
        assert self.model is not None
        self.model.compile(loss='mse', optimizer=Adam(lr=self.learning_rate))

    def save_trained_model(self):
        """
        Save the trained neural network under a fixed name specific for this trader.
        """
        save_keras_sequential(self.model, 'trading', self.name)
        logger.info(f"DQL Trader: Saved trained model")

    def get_action(self, state: State) -> (float, float):
        """
        Get best action for current state, either randomly or predicted from the neural network.
        The choice between random and neural network solely depends on epsilon:
        Epsilon is the probability of a random action.

        Args:
            state: The state to use
        Returns:
            A pair of floats encoding the stock actions
        """
        if self.train_while_trading and np.random.rand() <= self.epsilon:
            # Generate and return two random actions
            logger.debug(f"DQL Trader: Choose random actions")
            return random.choice(self.STOCK_ACTIONS)
        else:
            # Generate values per action by calling neural network with current state
            action_values = self.model.predict(state.to_model_input())
            logger.debug(f"DQL Trader: Use trained model to choose from {action_values}")
            # Get index with highest value (if there are more than one, get the first), and return corresponding actions
            index = np.argmax(action_values[0])
            logger.debug(f"DQL Trader: Choosen index: {index}")
            return self.STOCK_ACTIONS[index]

    def calculate_reward(self, last_portfolio_value: float, current_portfolio_value: float) -> float:
        """
        Implements the rewards function by comparing last portfolio value and current portfolio value.
        The reward will be positive if we gained portfolio value and negative if we lost portfolio value.
        This function overproportionally rewards gains by squaring the positive returns.

        Args:
            last_portfolio_value: Last value of Portfolio
            current_portfolio_value: Current value of Portfolio
        Returns:
            The reward as float
        """
        if current_portfolio_value > last_portfolio_value:
            return ((current_portfolio_value / last_portfolio_value) * 10.0) ** 2
        elif current_portfolio_value == last_portfolio_value:
            return 0.0
        else:
            return -100.0

    def train_model(self):
        """
        Train the neural network using a small random batch of the stored experiences in memory.
        """
        # Take a random sample (of size batch_size) from our memory
        batch = random.sample(self.memory, self.batch_size)

        # Train the neural net by using the immediate reward as desired output (this ignores all future rewards)
        for state, actionA, actionB, reward, _ in batch:
            output_values = self.model.predict(state.to_model_input())
            index = self.STOCK_ACTIONS.index((actionA, actionB))
            logger.debug(
                f"DQL Trader: actionA: {actionA}, actionB: {actionB}, index of action to target: {index}, reward: {reward}")
            target_action_values = self.model.predict(state.to_model_input())
            target_action_values[0][index] = reward
            logger.debug(
                f"DQL Trader: Before training: Input {state.to_model_input()} Output {output_values} Expected {target_action_values}")

            # Finally train the model for one epoch
            self.model.fit(state.to_model_input(), target_action_values, batch_size=self.batch_size, epochs=1,
                           verbose=0)
            output_values = self.model.predict(state.to_model_input())
            logger.debug(
                f"DQL Trader: After training: Input {state.to_model_input()} Output {output_values} Expected {target_action_values}")

    def doTrade(self, portfolio: Portfolio, current_portfolio_value: float,
                stock_market_data: StockMarketData) -> OrderList:
        """
        Generate action to be taken on the "stock market"
    
        Args:
          portfolio : current Portfolio of this trader
          current_portfolio_value : value of Portfolio at given moment
          stock_market_data : StockMarketData for evaluation

        Returns:
          A OrderList instance, may be empty never None
        """
        # build current state object
        stock_a_data = stock_market_data[CompanyEnum.COMPANY_A]
        stock_b_data = stock_market_data[CompanyEnum.COMPANY_B]
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

        # Store experience and train the neural network only if doTrade was called before at least once
        if self.train_while_trading and self.last_state is not None:
            reward = self.calculate_reward(self.last_portfolio_value, current_portfolio_value)
            memory_tuple = (self.last_state, self.last_action_a, self.last_action_b, reward, current_state)
            self.memory.append(memory_tuple)
            if len(self.memory) > self.batch_size + self.min_size_of_memory_before_training:
                self.train_model()

        # Create actions for current state and decrease epsilon for fewer random actions
        (action_a, action_b) = self.get_action(current_state)
        self.epsilon = max([self.epsilon_min, self.epsilon * self.epsilon_decay])
        logger.debug(f"DQL Trader: Computed orders {action_a} and {action_b} with epsilon {self.epsilon}")

        # Save created state, actions and portfolio value for the next call of doTrade
        self.last_state, self.last_action_a, self.last_action_b = current_state, action_a, action_b
        self.last_portfolio_value = current_portfolio_value
        return self.create_order_list(action_a, action_b, portfolio, stock_market_data)

    def create_order_list(self, action_a: float, action_b: float,
                          portfolio: Portfolio, stock_market_data: StockMarketData) -> OrderList:
        """
        Take two floats between -1.0 and +1.0 (one for stock A and one for stock B) and convert them into corresponding
        orders.

        Args:
            action_a: float between -1.0 and 1.0, representing buy(positive) / sell(negative) for Company A
            action_b: float between -1.0 and 1.0, representing buy(positive) / sell(negative) for Company B
            portfolio: current portfolio of this trader
            stock_market_data: current stock market data

        Returns:
            List of corresponding orders
        """
        assert -1.0 <= action_a <= +1.0 and -1.0 <= action_b <= +1.0
        assert portfolio is not None and stock_market_data is not None
        order_list = OrderList()

        # Create orders for stock A
        owned_amount_a = portfolio.get_amount(CompanyEnum.COMPANY_A)
        if action_a > 0.0:
            current_price = stock_market_data.get_most_recent_price(CompanyEnum.COMPANY_A)
            amount_to_buy = int(action_a * (portfolio.cash // current_price))
            order_list.buy(CompanyEnum.COMPANY_A, amount_to_buy)
        if action_a < 0.0 and owned_amount_a > 0:
            amount_to_sell = int(abs(action_a) * owned_amount_a)
            order_list.sell(CompanyEnum.COMPANY_A, amount_to_sell)

        # Create orders for stock B
        owned_amount_b = portfolio.get_amount(CompanyEnum.COMPANY_B)
        if action_b > 0.0:
            current_price = stock_market_data.get_most_recent_price(CompanyEnum.COMPANY_B)
            amount_to_buy = int(action_b * (portfolio.cash // current_price))
            order_list.buy(CompanyEnum.COMPANY_B, amount_to_buy)
        if action_b < 0.0 and owned_amount_b > 0:
            amount_to_sell = int(abs(action_b) * owned_amount_b)
            order_list.sell(CompanyEnum.COMPANY_B, amount_to_sell)
        return order_list


# This method retrains the trader from scratch using training data from PERIOD_1 and test data from PERIOD_2
EPISODES = 50
if __name__ == "__main__":
    # Read the training data
    training_data = read_stock_market_data([CompanyEnum.COMPANY_A, CompanyEnum.COMPANY_B], [PERIOD_1])
    test_data = read_stock_market_data([CompanyEnum.COMPANY_A, CompanyEnum.COMPANY_B], [PERIOD_1, PERIOD_2])
    start_training_day, final_training_day = dt.date(2009, 1, 2), dt.date(2011, 12, 29)
    start_test_day, final_test_day = dt.date(2012, 1, 3), dt.date(2015, 12, 30)

    # Define initial portfolio
    name = 'DQL trader portfolio'
    portfolio = Portfolio(10000.0, [], name)

    # Initialize trader: use perfect predictors, don't use an already trained model, but learn while trading
    # trader = DqlTrader(PerfectPredictor(CompanyEnum.COMPANY_A), PerfectPredictor(CompanyEnum.COMPANY_B), False, True, DQLTRADER_PERFECT_PREDICTOR)
    # trader = DqlTrader(StockANnPerfectBinaryPredictor(), StockBNnPerfectBinaryPredictor(), False, True, DQLTRADER_PERFECT_NN_BINARY_PREDICTOR)
    trader = DqlTrader(StockANnBinaryPredictor(), StockBNnBinaryPredictor(), False, True, DQLTRADER_NN_BINARY_PREDICTOR)

    # Start evaluation and train correspondingly; don't display the results in a plot but display final portfolio value
    evaluator = PortfolioEvaluator([trader], False)
    final_values_training, final_values_test = [], []
    for i in range(EPISODES):
        logger.info(f"DQL Trader: Starting training episode {i}")
        all_portfolios_over_time = evaluator.inspect_over_time(training_data, [portfolio],
                                                               date_offset=start_training_day)
        portfolio_over_time = all_portfolios_over_time[name]
        final_values_training.append(
            portfolio_over_time[final_training_day].total_value(final_training_day, training_data))
        trader.save_trained_model()

        # Evaluation over training and visualization
        # trader_test = DqlTrader(PerfectPredictor(CompanyEnum.COMPANY_A), PerfectPredictor(CompanyEnum.COMPANY_B), True, False, DQLTRADER_PERFECT_PREDICTOR)
        # trader_test = DqlTrader(StockANnPerfectBinaryPredictor(), StockBNnPerfectBinaryPredictor(), True, False, DQLTRADER_PERFECT_NN_BINARY_PREDICTOR)
        trader_test = DqlTrader(StockANnBinaryPredictor(), StockBNnBinaryPredictor(), True, False,
                                DQLTRADER_NN_BINARY_PREDICTOR)
        evaluator_test = PortfolioEvaluator([trader_test], False)
        all_portfolios_over_time = evaluator_test.inspect_over_time(test_data, [portfolio], date_offset=start_test_day)
        portfolio_over_time = all_portfolios_over_time[name]
        final_values_test.append(portfolio_over_time[final_test_day].total_value(final_test_day, test_data))
        logger.info(f"DQL Trader: Finished training episode {i}, "
                    f"final portfolio value training {final_values_training[-1]} vs. "
                    f"final portfolio value test {final_values_test[-1]}")

    from matplotlib import pyplot as plt

    plt.figure()
    plt.plot(final_values_training, color="black")
    plt.plot(final_values_test, color="green")
    plt.title('final portfolio value training vs. final portfolio value test')
    plt.ylabel('final portfolio value')
    plt.xlabel('episode')
    plt.show()
