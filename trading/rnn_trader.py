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
from keras.models import Sequential
from keras.layers import Dense
from keras.optimizers import Adam
from trading.trader_interface import TradingActionEnum
from trading.trader_interface import CompanyEnum
from trading.trader_interface import SharesOfCompany

from utils import save_keras_sequential, load_keras_sequential

# Define possible actions per stock
STOCKACTIONS = [+1.0, +0.5, 0.0, -0.5, -1.0]


# Define state from the trader's viewpoint
class State:
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

    def input_array(self):
        return np.array(
            [[self.cash, self.stockA, self.stockB, self.priceA, self.priceB, self.predictedA, self.predictedB]])


class RnnTrader(ITrader):
    '''
    Implementation of ITrader based on Reinforced Neural Network (RNN): doTrade generates TradingActionList according to last generated changes on Portfolio value.
    '''
    MODEL_FILE_NAME = 'rnn_trader'

    def __init__(self, stockAPredictor: IPredictor, stockBPredictor: IPredictor):
        '''
        Constructor
        '''
        # Save predictors
        self.stockAPredictor = stockAPredictor
        self.stockBPredictor = stockBPredictor

        # Hyperparameters for neural network
        self.state_size = 7  # TODO: infer from...?
        # Discretization of actions as list of (+1.0,+1.0), (+1.0, +0.5), (+1.0, 0.0), ..., (-1.0, -1.0)
        # We have 5 actions per stock (+1.0, +0.5, 0.0, -0.5, -1.0)
        # Means 25 actions for our two stocks
        self.action_size = len(STOCKACTIONS) * len(STOCKACTIONS)  # TODO: infer from ...?
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

    def save_model(self):
        """
        Saves model in file system
        """
        save_keras_sequential(self.model, 'trading', self.MODEL_FILE_NAME)

    def load_model(self) -> Sequential:
        """
        Load model from Fflesystem 
        """
        return load_keras_sequential('trading', self.MODEL_FILE_NAME)

    # Get best action for current state, either randomly or predicted from neural network
    # Choice between random and neural network solely depends on epsilon
    # Epsilon is the probability of a random action
    # Return value is two floats between -1.0 and +1.0
    # First float is for action on stock A, second float is for action on stock B
    # Minus means "sell stock proportionally to owned amount", e.g. -0.5 means "sell half of your owned stock"
    # Plus means "buy stock proportionally to owned cash", e.g. +0.5 means "take half of your cash and by that stock"
    # ATTENTION: if sum of action over all stocks is greater than 1.0, then not all stocks can be bought!
    # Example: action stock A = +1.0 and action stock B = +0.2
    # This leads to all cash to be spent on buying stock A (because of action +1.0),
    # which in turn means there is no cash left to buy stock B (the action +0.2)
    def get_action(self, state: State):
        if np.random.rand() <= self.epsilon:
            # generate two random actions
            return random.choice(STOCKACTIONS), random.choice(STOCKACTIONS)
        else:
            # generate values per action by calling neural network with current state
            actionValues = self.model.predict(state.input_array())
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

    # decreases epsilon by one step (decay), but not lower than its defined minimum
    def decrease_epsilon(self):
        self.epsilon = max([self.epsilon_min, self.epsilon * self.epsilon_decay])

    # TODO description
    # Implements rewards function
    # TODO implement reward using discounted future values as well
    def calculateReward(self, lastPortfolioValue: float, currentPortfolioValue: float) -> int:
        assert lastPortfolioValue is not None
        assert currentPortfolioValue is not None

        if (currentPortfolioValue > lastPortfolioValue):
            return 1
        elif (currentPortfolioValue < lastPortfolioValue):
            return -1
        else:
            return 0

    # TODO pick samples randomly from replay memory (with batch_size)
    def train_model(self):
        if len(self.memory) < self.train_start:  # TODO check whether train_start is necessary
            return
        batch_size = min(self.batch_size, len(self.memory))  # TODO check with train_start
        minibatch = random.sample(self.memory, batch_size)

        for state, actionA, actionB, reward, nextState in minibatch:
            assert isinstance(state, State)
            state.print()
            target = reward  # TODO also take future rewards into account using gamma

            self.model.fit(state.input_array(), target, epochs=1, verbose=1)

            # transform input data to input of neural network
            # input_values = []
            # for tuple in minibatch:
            #     input_values.append([tuple[i]])
            #
            # # calculate target values for neural network
            #
            # update_input = np.zeros((batch_size, self.state_size))
            # update_target = np.zeros((batch_size, self.state_size))
            # action, reward, done = [], [], []
            #
            # for i in range(self.batch_size):
            #     update_input[i] = mini_batch[i][0]
            #     action.append(mini_batch[i][1])
            #     reward.append(mini_batch[i][2])
            #     update_target[i] = mini_batch[i][3]
            #     done.append(mini_batch[i][4])
            #
            # target = self.model.predict(update_input)


            # target_val = self.target_model.predict(update_target)

            # for i in range(self.batch_size):
            #     # Q Learning: get maximum Q value at s' from target model
            #     if done[i]:
            #         target[i][action[i]] = reward[i]
            #     else:
            #         target[i][action[i]] = reward[i] + self.discount_factor * (
            #             np.amax(target_val[i]))

            # and do the model fit!
            # loss = self.model.fit(update_input, target, batch_size=self.batch_size, epochs=1, verbose=1)

    # TODO why company names as parameters? we don't use them
    # TODO let ILSE give us information whether both (all) previous trades succeeded
    # TODO maybe get rid of currentPortfolioValue, because this is easily computable from the portfolio
    def doTrade(self, portfolio: Portfolio, currentPortfolioValue: float,
                stockMarketData: StockMarketData) -> TradingActionList:
        """ Generate action to be taken on the "stock market"
    
        Args:
          portfolio : current Portfolio of this trader
          currentPortfolioValue : value of Portfolio at given Momemnt
          stockMarketData : StockMarketData for evaluation
        Returns:
          A TradingActionList instance, may be empty never None
        """
        # build current state object
        predictedValueStockA = self.stockAPredictor.doPredict(
            stockMarketData.get_stock_data_for_company(CompanyEnum.COMPANY_A))
        predictedValueStockB = self.stockBPredictor.doPredict(
            stockMarketData.get_stock_data_for_company(CompanyEnum.COMPANY_B))
        current_state = State(portfolio.cash,
                              portfolio.get_amount(CompanyEnum.COMPANY_A.value),
                              portfolio.get_amount(CompanyEnum.COMPANY_B.value),
                              stockMarketData.get_most_recent_price(CompanyEnum.COMPANY_A.value),
                              stockMarketData.get_most_recent_price(CompanyEnum.COMPANY_B.value),
                              predictedValueStockA,
                              predictedValueStockB)

        if self.lastState is not None:  # doTrade was called before at least once
            assert self.lastActionA is not None and self.lastActionB is not None and self.lastPortfolioValue is not None
            # baue memory tuple auf
            reward = self.calculateReward(self.lastPortfolioValue, currentPortfolioValue)
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
        self.lastPortfolioValue = currentPortfolioValue
        self.lastState = current_state
        return self.create_TradingActionList(actionA, actionB, portfolio, stockMarketData)

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

        mostRecentPriceCompanyA = stockMarketData.get_most_recent_price(CompanyEnum.COMPANY_A.value)
        tradingActionA = self.create_TradingAction(CompanyEnum.COMPANY_A, actionA, currentPortfolio,
                                                   mostRecentPriceCompanyA)
        if (tradingActionA is not None):
            result.addTradingAction(tradingActionA)

        mostRecentPriceCompanyB = stockMarketData.get_most_recent_price(CompanyEnum.COMPANY_B.value)
        tradingActionB = self.create_TradingAction(CompanyEnum.COMPANY_B, actionB, currentPortfolio,
                                                   mostRecentPriceCompanyB)
        if (tradingActionB is not None):
            result.addTradingAction(tradingActionB)

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

            sharesOfCompanyToBuy = SharesOfCompany(companyEnum.value, amountOfSharesOfComapanyToBuy)

            return TradingAction(TradingActionEnum.BUY, sharesOfCompanyToBuy)

        elif (action < 0.0):
            # Get amount of shares we own; it may be 0
            amountOfSharesWeOwn = currentPortfolio.get_amount(companyEnum.value)
            assert amountOfSharesWeOwn >= 0
            # Percent of shares to sell multiply by number of owned actions
            amountOfSharesToSell = int(abs(action) * amountOfSharesWeOwn)
            # Wrap into SharesOfCompany object TODO do we need this?
            sharesOfCompanyToSell = SharesOfCompany(companyEnum.value, amountOfSharesToSell)
            return TradingAction(TradingActionEnum.SELL, sharesOfCompanyToSell)
        else:
            # TODO: use Logging!!!
            print(f"!!!! RnnTrader - INFO: Trading action is None, action: {action}, Portfolio: {currentPortfolio}")

        return None

    def isTradingActionListValid(self, tradingActionList: TradingActionList, currentPortfolio: Portfolio,
                                 stockMarketData: StockMarketData) -> bool:
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

        isValid, currentCash = self.isTradingActionValid(currentCash, CompanyEnum.COMPANY_A.value,
                                                         tradingActionForCompanyA, mostRecentPriceCompanyA,
                                                         currentPortfolio)
        if (isValid is False):
            return False

        mostRecentPriceCompanyB = stockMarketData.get_most_recent_price(CompanyEnum.COMPANY_B.value)
        tradingActionForCompanyB = tradingActionList.get_by_CompanyEnum(CompanyEnum.COMPANY_B)

        isValid, currentCash = self.isTradingActionValid(currentCash, CompanyEnum.COMPANY_B.value,
                                                         tradingActionForCompanyB, mostRecentPriceCompanyB,
                                                         currentPortfolio)
        if (isValid is False):
            return False

        return True

    def isTradingActionValid(self, currentCash: float, companyName: str, tradingActionForCompany: TradingAction,
                             mostRecentPriceCompany: float, currentPortfolio: Portfolio):
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
        if (tradingActionForCompany is not None):
            if (tradingActionForCompany.action == TradingActionEnum.BUY):
                priceToPay = mostRecentPriceCompany * tradingActionForCompany.shares

                currentCash = currentCash - priceToPay
                if (currentCash < 0):
                    # TODO: use Logging!!!
                    print(
                        f"!!!! RnnTrader - WARNING: Not enough money to pay! tradingActionForCompany: {tradingActionForCompany}, Portfolio: {currentPortfolio}")
                    return False, currentCash

            elif (tradingActionForCompany.action == TradingActionEnum.SELL):
                if (tradingActionForCompany.shares > currentPortfolio.get_amount(companyName)):
                    return False
            else:
                raise ValueError(f'Action for tradingActionForCompanyB is not valid: {tradingActionForCompany}')

        return True, currentCash


# Train the trader and its respective neural network(s)
from evaluating.portfolio_evaluator import PortfolioEvaluator
from evaluating.evaluator import read_stock_market_data

EPISODES = 2
if __name__ == "__main__":
    # Reading training data
    training_data = read_stock_market_data([[CompanyEnum.COMPANY_A.value, CompanyEnum.COMPANY_A.value + '_1962-2011'],
                                            [CompanyEnum.COMPANY_B.value, CompanyEnum.COMPANY_B.value + '_1962-2011']])

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
