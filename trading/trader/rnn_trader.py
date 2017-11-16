'''
Created on 13.11.2017

@author: jtymoszuk
'''
import random
from collections import deque
import numpy as np

from utils import read_stock_market_data
from evaluating.portfolio_evaluator import PortfolioEvaluator
from model import Portfolio, StockMarketData
from predicting.model.IPredictor import IPredictor
from predicting.predictor.simple_predictor import SimplePredictor
from trading.model.ITrader import ITrader
from trading.model.trader_interface import TradingActionList, TradingAction
from keras.models import Sequential
from keras.layers import Dense
from keras.optimizers import Adam
from trading.model.trader_interface import TradingActionEnum
from trading.model.trader_interface import CompanyEnum
from trading.model.trader_interface import SharesOfCompany

from utils import save_keras_sequential, load_keras_sequential

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



class RnnTrader(ITrader):
    '''
    Implementation of ITrader based on Reinforced Neural Network (RNN): doTrade generates TradingActionList according to last generated changes on Portfolio value.
    '''
    MODEL_FILE_NAME = 'rnn_trader'

    def __init__(self, stock_a_predictor: IPredictor, stock_b_predictor: IPredictor, learnFromTrades: bool = False):
        '''
        Constructor
        '''
        # Save predictors and whether we learn from subsequent trades
        self.stock_a_predictor = stock_a_predictor
        self.stock_b_predictor = stock_b_predictor
        self.learnFromTrades = learnFromTrades

        # Hyperparameters for neural network
        self.state_size = 7  # TODO: infer from...?
        # Discretization of actions as list of (+1.0,+1.0), (+1.0, +0.5), (+1.0, 0.0), ..., (-1.0, -1.0)
        # We have 5 actions per stock (+1.0, +0.5, 0.0, -0.5, -1.0)
        # Means 25 actions for our two stocks
        self.action_size = len(STOCKACTIONS) * len(STOCKACTIONS)
        self.hidden_size = 50

        # These are hyper parameters for the DQN
        self.discount_factor = 0.99
        self.learning_rate = 0.001
        self.epsilon = 1.0
        self.epsilon_decay = 0.999
        self.epsilon_min = 0.01
        self.batch_size = 2  # TODO war mal 64
        self.train_start = 1000
        # create replay memory using deque
        self.memory = deque(maxlen=2000)

        # create main model, either from file or (if not existent) from scratch
        self.model = self.load_model()
        if (self.model is None):
            self.model = self.build_model()

        # create and initialize target model
        # self.target_model = self.build_model()
        # self.update_target_model()

        self.lastPortfolioValue = None
        self.lastActionA = None
        self.lastActionB = None
        self.lastState = None

    # Destructor
    def __del__(self):
        if self.learnFromTrades:
            save_keras_sequential(self.model, 'trading', self.MODEL_FILE_NAME)

    # TODO description
    def build_model(self) -> Sequential:
        model = Sequential()
        model.add(
            Dense(self.hidden_size, input_dim=self.state_size, activation='relu', kernel_initializer='he_uniform'))
        model.add(Dense(self.hidden_size, activation='relu', kernel_initializer='he_uniform'))
        # activation=tanh for output between -1 and +1
        model.add(Dense(self.action_size, activation='relu', kernel_initializer='he_uniform'))
        # model.summary()
        model.compile(loss='mse', optimizer=Adam(lr=self.learning_rate))
        return model

    # TODO remove this method?
    def load_model(self) -> Sequential:
        """
        Load model from file system
        """
        return load_keras_sequential('trading', self.MODEL_FILE_NAME)


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
            # generate two random actions
            return random.choice(STOCKACTIONS), random.choice(STOCKACTIONS)
        else:
            # generate values per action by calling neural network with current state
            actionValues = self.model.predict(state.get_input_array())
            # Get index with highest value and return corresponding actions
            index = np.argmax(actionValues[0])  # TODO what if there are more actions with the same values?
            return self.get_actions_from_index(index)

    def get_actions_from_index(self, index: int):
        assert 0 <= index < self.action_size
        return STOCKACTIONS[index // len(STOCKACTIONS)], STOCKACTIONS[index % len(STOCKACTIONS)]

    def get_index_from_actions(self, actionA: float, actionB: float):
        assert actionA in STOCKACTIONS
        assert actionB in STOCKACTIONS
        return STOCKACTIONS.index(actionA) * len(STOCKACTIONS) + STOCKACTIONS.index(actionB)

    # TODO save sample <s,a,r,s'> to the replay memory
    # TODO do we really need this function?
    def append_sample(self, state: State, actionA: float, actionB: float, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def decrease_epsilon(self):
        """
        Decreases epsilon by one step (decay), but not lower than its defined minimum
        """
        self.epsilon = max([self.epsilon_min, self.epsilon * self.epsilon_decay])

    # TODO implement reward using discounted future values as well
    def calculateReward(self, last_portfolio_value: float, current_portfolio_value: float) -> int:
        """
        Implements rewards function
        
        Args:
            last_portfolio_value - last value of Portfolio
            current_portfolio_value - current value of Portfolio
        """
        assert last_portfolio_value is not None
        assert current_portfolio_value is not None

        if (current_portfolio_value > last_portfolio_value):
            return 1
        elif (current_portfolio_value < last_portfolio_value):
            return -1
        else:
            return 0

    # TODO pick samples randomly from replay memory (with batch_size)
    def train_model(self):
        if len(self.memory) < self.train_start:  # TODO check whether train_start is necessary
            return
        batch_size = min(self.batch_size, len(self.memory))  # TODO check with train_start
        batch = random.sample(self.memory, batch_size)

        for state, actionA, actionB, reward, nextState in batch:
            assert isinstance(state, State)
            state.print()
            target = reward  # TODO also take future rewards into account using gamma

            # build target action values and exchange value for the choosen actions
            target_action_values = self.model.predict(state.get_input_array())
            index = self.get_index_from_actions(actionA, actionB)
            target_action_values[0][index] = target

            # finally train the model for one epoch
            self.model.fit(state.get_input_array(), target_action_values, batch_size=self.batch_size, epochs=1, verbose=1)

    # TODO why company names as parameters? we don't use them
    # TODO let ILSE give us information whether both (all) previous trades succeeded
    # TODO maybe get rid of currentPortfolioValue, because this is easily computable from the portfolio
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
        predictedValueStockA = self.stock_a_predictor.doPredict(
            stock_market_data.get_stock_data_for_company(CompanyEnum.COMPANY_A))
        predictedValueStockB = self.stock_b_predictor.doPredict(
            stock_market_data.get_stock_data_for_company(CompanyEnum.COMPANY_B))
        current_state = State(portfolio.cash,
                              portfolio.get_amount(CompanyEnum.COMPANY_A),
                              portfolio.get_amount(CompanyEnum.COMPANY_B),
                              stock_market_data.get_most_recent_price(CompanyEnum.COMPANY_A),
                              stock_market_data.get_most_recent_price(CompanyEnum.COMPANY_B),
                              predictedValueStockA,
                              predictedValueStockB)

        if self.lastState is not None:  # doTrade was called before at least once
            assert self.lastActionA is not None and self.lastActionB is not None and self.lastPortfolioValue is not None
            # baue memory tuple auf
            reward = self.calculateReward(self.lastPortfolioValue, current_portfolio_value)
            memoryTuple = (self.lastState, self.lastActionA, self.lastActionB, reward, current_state)
            # memory tuple speichern
            self.memory.append(memoryTuple)
            # wir nehmen zufällige Teilmenge von memory und trainieren model mit obiger Teilmenge
            self.train_model()

        # Create actions for current state
        actionA, actionB = self.get_action(current_state)
        # Decrease epsilon for fewer random actions
        self.decrease_epsilon()
        # Save created actions for the next call of doTrade
        self.lastActionA = actionA
        self.lastActionB = actionB
        self.lastPortfolioValue = current_portfolio_value
        self.lastState = current_state
        return self.create_TradingActionList(actionA, actionB, portfolio, stock_market_data)

    def create_TradingActionList(self, actionA: float, actionB: float, currentPortfolio: Portfolio,
                                 stockMarketData: StockMarketData) -> TradingActionList:
        """
        Creates TradingActionList for later Evaluation
        Args:
          actionA : float value between -1.0 and 1.0, representing operation (Buy=positive or Sell=negative) and percentage of shares to consider for Company A
          actionB : float value between -1.0 and 1.0, representing operation (Buy=positive or Sell=negative) and percentage of shares to consider for Company B
          currentPortfolio : current Portfolio of this Trader
          stockMarketData: StockMarketData
        Returns:
          A TradingActionList instance, may be empty never None
        """
        result = TradingActionList()

        mostRecentPriceCompanyA = stockMarketData.get_most_recent_price(CompanyEnum.COMPANY_A)
        tradingActionA = self.create_TradingAction(CompanyEnum.COMPANY_A, actionA, currentPortfolio,
                                                   mostRecentPriceCompanyA)
        result.add_trading_action(tradingActionA)

        mostRecentPriceCompanyB = stockMarketData.get_most_recent_price(CompanyEnum.COMPANY_B)
        tradingActionB = self.create_TradingAction(CompanyEnum.COMPANY_B, actionB, currentPortfolio,
                                                   mostRecentPriceCompanyB)
        result.add_trading_action(tradingActionB)

        return result

    def create_TradingAction(self, companyEnum: CompanyEnum, action: float, currentPortfolio: Portfolio,
                             mostRecentPriceCompany: float) -> TradingAction:
        """
        Creates single TradingAction for later evaluation in Stock Market
        Args:
          companyEnum : CompanyEnum describes current Company
          action : float value between -1.0 and 1.0, representing operation (Buy=positive or Sell=negative) and percentage of shares to consider for given Company
          currentPortfolio : current Portfolio of this Trader
          mostRecentPriceCompany: most recent price of given company on stock market as float
        Returns:
          A TradingAction instance, may be None
        """
        assert action >= -1.0 and action <= 1.0

        if (action > 0.0):
            possibleAmountOfUnitsToBuy = int(currentPortfolio.cash // mostRecentPriceCompany)

            amountOfSharesOfComapanyToBuy = int(action * possibleAmountOfUnitsToBuy)

            sharesOfCompanyToBuy = SharesOfCompany(companyEnum, amountOfSharesOfComapanyToBuy)

            return TradingAction(TradingActionEnum.BUY, sharesOfCompanyToBuy)

        elif (action < 0.0):
            # Get amount of shares we own; it may be 0
            amountOfSharesWeOwn = currentPortfolio.get_amount(companyEnum)
            assert amountOfSharesWeOwn >= 0
            # Percent of shares to sell multiply by number of owned actions
            amountOfSharesToSell = int(abs(action) * amountOfSharesWeOwn)
            # Wrap into SharesOfCompany object TODO do we need this?
            sharesOfCompanyToSell = SharesOfCompany(companyEnum, amountOfSharesToSell)
            return TradingAction(TradingActionEnum.SELL, sharesOfCompanyToSell)
        else:
            # TODO: use Logging!!!
            print(f"!!!! RnnTrader - INFO: Trading action is None, action: {action}, Portfolio: {currentPortfolio}")

        return None


EPISODES = 2
if __name__ == "__main__":
    # Reading training data
    training_data = read_stock_market_data([[CompanyEnum.COMPANY_A, CompanyEnum.COMPANY_A.value + '_1962-2011'],
                                            [CompanyEnum.COMPANY_B, CompanyEnum.COMPANY_B.value + '_1962-2011']])

    # Define initial portfolio
    initial_portfolio = Portfolio(50000.0, [], 'RNN trader portfolio')

    # Define this trader, thereby loading trained networks
    trader = RnnTrader(SimplePredictor(), SimplePredictor())

    # Start evaluation and thereby learn training data
    evaluator = PortfolioEvaluator([trader], True)
    for i in range(EPISODES):
        evaluator.inspect_over_time(training_data, [initial_portfolio])

    # Save trained neural network
    trader.save_model()
