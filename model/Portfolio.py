from typing import List

import copy
import datetime

from model import StockMarketData
from model.SharesOfCompany import SharesOfCompany
from model.CompanyEnum import CompanyEnum
from model.trader_actions import TradingActionList, TradingActionEnum, TradingAction
from logger import logger

SharesList = List[SharesOfCompany]


class Portfolio:
    """
    Represents portfolio of a client
    """

    def __init__(self, cash: float, shares: SharesList, name: str = 'nameless'):
        """ Constructor

        Args:
          cash: The portfolio's initial cash level
          shares: The portfolio's initial list of shares
          name: The portfolio's name. This is mainly used as diagram legends in `PortfolioEvaluator#draw`
        """
        self.cash = cash
        self.shares = shares
        self.name = name

    def total_value(self, date: datetime.date, prices: StockMarketData):
        """
        Calculates the portfolio's total value based on the held shares multiplied by their current value added to the
        cash level.

        Returns:
            The portfolio's total value
        """
        values = [share.amount *
                  [price[1] for price in prices.get_for_company(share.company_enum).iter() if date == price[0]][0]
                  for share in self.shares]

        return sum(values) + self.cash

    def __has_stock(self, company_enum: CompanyEnum):
        """
        Checks whether the stock by the given `company_enum` is held in the portfolio
        Args:
            company_enum: The company to check the stock existence for

        Returns:
            `True` if existing, `False` otherwise
        """
        return len(self.shares) != 0 and len(
            [share for share in self.shares if share.company_enum == company_enum]) != 0

    def get_or_insert(self, company_enum: CompanyEnum):
        """
        If the portfolios holds a stock of `company_enum` this is returned. Otherwise an initial object with 0 shares
        held is inserted.

        Args:
            company_enum: The company to get/insert the stock count for

        Returns:
            An object of type `SharesOfCompany` of this `company_enum`, either with intial share count of 0 or the
            actual share count
        """
        if not self.__has_stock(company_enum):
            share = SharesOfCompany(company_enum, 0)
            self.shares.append(share)
            return share

        return next(share for share in self.shares if share.company_enum == company_enum)

    def __get_by_name(self, company_enum: CompanyEnum) -> SharesOfCompany:
        """
        Returns SharesOfCompany for `company_enum`, or None if nothing found
        """
        return next((share for share in self.shares if share.company_enum == company_enum), None)

    def get_amount(self, company_enum: CompanyEnum) -> int:
        """
        Return the amount of shares we hold from the given `company_enum`.  If the portfolio doesn't hold any shares of
        this company, 0 ist returned
        """
        share = self.__get_by_name(company_enum)
        if share is not None:
            return share.amount
        else:
            return 0

    def update(self, stock_market_data: StockMarketData, trade_action_list: TradingActionList):
        """
        Iterates through the list of trading actions (`trade_action_list`), applies those actions and returns an updated
        `Portfolio` object based on the given `StockMarketData`. If `trade_action_list` is empty nothing will be changed

        Args:
            stock_market_data: The market data based on which the actions are applied
            trade_action_list: The list of trading action to apply

        Returns:
            An updated portfolio. This is a deep copy of the given `portfolio` (see `copy.deepcopy`)
        """
        updated_portfolio = copy.deepcopy(self)

        logger.debug(f"\nUpdate portfolio {self.name}")

        if trade_action_list.is_empty():
            logger.info("trade_action_list.is_empty -> No action this time")
            return updated_portfolio

        for trade_action in trade_action_list.iterator():
            company_enum = trade_action.shares.company_enum

            current_date = stock_market_data.get_most_recent_trade_day()
            current_price = stock_market_data.get_most_recent_price(company_enum)

            logger.debug(f"Available cash on {current_date}: {updated_portfolio.cash}")
            # for share in update.shares:
            share = updated_portfolio.get_or_insert(company_enum)
            # if share.name is update.shares.name:
            amount = trade_action.shares.amount
            trade_volume = amount * current_price

            if trade_action.action is TradingActionEnum.BUY:
                logger.debug(f"Buying {amount} shares of '{share.company_enum}' with an individual value of "
                             f"{current_price}")
                logger.debug(f"  Volume of this trade: {trade_volume}")

                if trade_volume <= updated_portfolio.cash:
                    share.amount += amount
                    updated_portfolio.cash -= trade_volume
                else:
                    logger.warning(f"No sufficient cash reserve ({updated_portfolio.cash}) for planned transaction "
                                   f"with volume of {trade_volume}")
            elif trade_action.action is TradingActionEnum.SELL:
                logger.debug(f"Selling {amount} shares of {share.company_enum} with individual value of "
                             f"{current_price}")
                logger.debug(f"  Volume of this trade: {trade_volume}")

                if share.amount >= amount:
                    share.amount -= amount
                    updated_portfolio.cash += trade_volume
                else:
                    logger.warning(f"Not sufficient shares in portfolio ({amount}) for planned sale of {share.amount} "
                                   f"shares")

            logger.debug(f"Resulting available cash after trade: {updated_portfolio.cash}")

            total_portfolio_value = updated_portfolio.total_value(current_date, stock_market_data)
            logger.debug(f"Total portfolio value after trade: {total_portfolio_value}")

        return updated_portfolio

    def isTradingActionListValid(self, trading_action_list: TradingActionList,
                                 stock_market_data: StockMarketData) -> bool:
        """
        Validates if generated TradingActionList is valid in comparison to current Portfolio

        Args:
          trading_action_list: TradingActionList containing generated TradingActions to be sent into Evaluation (Stock Market)
          stock_market_data: StockMarketData containing date for all companies

        Returns:
          `True` if given TradingActionList is valid in comparison to current Portfolio, `False` otherwise, never None
        """

        current_cash = self.cash

        most_recent_price_company_a = stock_market_data.get_most_recent_price(CompanyEnum.COMPANY_A)
        trading_action_for_company_a = trading_action_list.get_by_CompanyEnum(CompanyEnum.COMPANY_A)

        is_valid, current_cash = self.__is_trading_action_valid(current_cash, CompanyEnum.COMPANY_A,
                                                                trading_action_for_company_a,
                                                                most_recent_price_company_a)
        if is_valid is False:
            return False

        most_recent_price_company_b = stock_market_data.get_most_recent_price(CompanyEnum.COMPANY_B)
        trading_action_for_company_b = trading_action_list.get_by_CompanyEnum(CompanyEnum.COMPANY_B)

        is_valid, current_cash = self.__is_trading_action_valid(current_cash, CompanyEnum.COMPANY_B,
                                                                trading_action_for_company_b,
                                                                most_recent_price_company_b)
        if is_valid is False:
            return False

        return True

    def __is_trading_action_valid(self, current_cash: float, company_enum: CompanyEnum,
                                  trading_action_for_company: TradingAction, most_recent_price_company: float):
        """
        Validates if given TradingAction is valid

        Args:
          current_cash: TradingActionList containing generated TradingAction's to be sent into Evaluation (Stock Market)
          company_enum: CCompanyEnum
          trading_action_for_company: TradingAction
          most_recent_price_company: most recent price of company as float

        Returns:
          A True if given TradingAction is valid in comparison to current Portfolio and Cash, False otherwise, never None
        """
        if trading_action_for_company is not None:
            if trading_action_for_company.action == TradingActionEnum.BUY:
                price_to_pay = most_recent_price_company * trading_action_for_company.shares

                current_cash = current_cash - price_to_pay
                if current_cash < 0:
                    logger.warning(
                        f"Not enough money to pay! tradingActionForCompany: "
                        f"{trading_action_for_company}, Portfolio: {self}")
                    return False, current_cash

            elif trading_action_for_company.action == TradingActionEnum.SELL:
                if trading_action_for_company.shares > self.get_amount(company_enum):
                    return False
            else:
                raise ValueError(f'Action for tradingActionForCompanyB is not valid: {trading_action_for_company}')

        return True, current_cash
