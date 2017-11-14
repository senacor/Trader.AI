'''
Created on 13.11.2017

@author: jtymoszuk
'''

from trading.trader_interface import Portfolio
from trading.trader_interface import ITrader
from trading.trader_interface import StockMarketData
from trading.trader_interface import TradingActionList
from keras.models import Sequential
from keras.layers import Dense
from keras.optimizers import sgd


class RnnTrader(ITrader):
    '''
    Implementation of ITrader based on Reinforced Neural Network (RNN): doTrade generates TradingActionList according to last generated changes on Portfolio value.
    '''

    def __init__(self):
        '''
        Constructor
        '''
        self.lastPortfolioValue = None
        
        hidden_size = 100
        
        # Input Size is defined by attributes of Portfolio and current and predicted values: 
        # 1. cash 
        # 2. amount of Shares Company A 
        # 3. current price Company A 
        # 4. Predicted price Company A 
        # 5. amount of Shares Company B 
        # 6. current price Company B 
        # 7. Predicted price Company A
        # => Number of inputs = 7
        NUMBER_OF_INPUTS = 7
        
        # Output:
        # 1. Buy/Sell Company A
        # 2. Amount of shares Company A
        # 3. Buy/Sell Company B
        # 4. Amount of shares Company B
        # => Number of Outputs = 4
        NUMBER_OF_OUTPUTS= 4
        
        self.model = Sequential()
        self.model.add(Dense(hidden_size, input_shape=(NUMBER_OF_INPUTS,), activation='relu'))
        self.model.add(Dense(hidden_size, activation='relu'))
        self.model.add(Dense(NUMBER_OF_OUTPUTS))
        self.model.compile(sgd(lr=.2), "mse")

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
