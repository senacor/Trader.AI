"""
Created on 19.11.2017

@author: rmueller
"""
from collections import deque
import datetime as dt

from definitions import PERIOD_1, PERIOD_2
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

TEAM_NAME = "team_green"

MODEL_FILENAME_DQLTRADER_PERFECT_PREDICTOR = TEAM_NAME + '_dql_trader_perfect'
MODEL_FILENAME_DQLTRADER_PERFECT_NN_BINARY_PREDICTOR = TEAM_NAME + '_dql_trader_perfect_nn_binary'
MODEL_FILENAME_DQLTRADER_NN_BINARY_PREDICTOR = TEAM_NAME + '_dql_trader_nn_binary'


class TeamGreenDqlTrader(ITrader):
    """
    Implementation of ITrader based on reinforced Q-learning (RQL).
    """
    RELATIVE_DATA_DIRECTORY = 'trading/trader/' + TEAM_NAME + '/' + TEAM_NAME + '_dql_trader_data'

    def __init__(self, stock_a_predictor: IPredictor, stock_b_predictor: IPredictor,
                 load_trained_model: bool=True,
                 train_while_trading: bool=False, network_filename: str=MODEL_FILENAME_DQLTRADER_NN_BINARY_PREDICTOR):
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
        self.network_filename = network_filename

        # Parameters for neural network
        self.state_size = 2
        self.action_size = 10
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

        # Create main model, either as trained model (from file) or as untrained model (from scratch)
        self.model = None
        if load_trained_model:
            logger.debug(f"DQL Trader: Try to load trained model")
            self.model = load_keras_sequential(self.RELATIVE_DATA_DIRECTORY, self.network_filename)
        if self.model is None:  # loading failed or we didn't want to use a trained model
            self.model = Sequential()
            self.model.add(Dense(self.hidden_size * 2, input_dim=self.state_size, activation='relu'))
            self.model.add(Dense(self.hidden_size, activation='relu'))
            self.model.add(Dense(self.action_size, activation='linear'))
            logger.info(f"DQL Trader: Created new untrained model")
        assert self.model is not None
        self.model.compile(loss='mse', optimizer=Adam(lr=self.learning_rate))

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
        # TODO: Build and store current state object

        # TODO: Store experience and train the neural network only if doTrade was called before at least once

        # TODO: Create actions for current state and decrease epsilon for fewer random actions

        # TODO: Save created state, actions and portfolio value for the next call of doTrade

        return OrderList()

    def save_trained_model(self):
        """
        Save the trained neural network under a fixed name specific for this trader.
        """
        save_keras_sequential(self.model, self.RELATIVE_DATA_DIRECTORY, self.network_filename)


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
    # trader = DqlTrader(PerfectPredictor(CompanyEnum.COMPANY_A), PerfectPredictor(CompanyEnum.COMPANY_B), False, True, MODEL_FILENAME_DQLTRADER_PERFECT_PREDICTOR)
    # trader = DqlTrader(StockANnPerfectBinaryPredictor(), StockBNnPerfectBinaryPredictor(), False, True, MODEL_FILENAME_DQLTRADER_PERFECT_NN_BINARY_PREDICTOR)
    trader = TeamGreenDqlTrader(StockANnBinaryPredictor(), StockBNnBinaryPredictor(), False, True, MODEL_FILENAME_DQLTRADER_NN_BINARY_PREDICTOR)

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
        # trader_test = TeamGreenDqlTrader(PerfectPredictor(CompanyEnum.COMPANY_A), PerfectPredictor(CompanyEnum.COMPANY_B), True, False, MODEL_FILENAME_DQLTRADER_PERFECT_PREDICTOR)
        # trader_test = TeamGreenDqlTrader(StockANnPerfectBinaryPredictor(), StockBNnPerfectBinaryPredictor(), True, False, MODEL_FILENAME_DQLTRADER_PERFECT_NN_BINARY_PREDICTOR)
        trader_test = TeamGreenDqlTrader(StockANnBinaryPredictor(), StockBNnBinaryPredictor(), True, False, MODEL_FILENAME_DQLTRADER_NN_BINARY_PREDICTOR)
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
