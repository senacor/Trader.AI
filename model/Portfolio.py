import copy
import datetime

from model import StockMarketData
from model.SharesOfCompany import SharesOfCompany
from model.CompanyEnum import CompanyEnum
from trading.model.trader_interface import TradingActionList, TradingActionEnum, TradingAction


class Portfolio:
    """
    Represents portfolio of a client
    """

    def __init__(self, cash: float, shares: list, name: str = 'nameless'):
        """ Constructor

        Args:
          cash : current cash level
          shares : list of SharesOfCompany, see SharesOfCompany
        """
        self.name = name  # TODO wo brauchen wir name?
        self.cash = cash
        self.shares = shares

    def total_value(self, date: datetime.date, prices: dict):
        values = [share.amount *
                  [price[1] for price in prices[share.company_enum] if date == price[0]][0]
                  for share in self.shares]

        return sum(values) + self.cash

    def has_stock(self, company_enum: CompanyEnum):
        return len(self.shares) != 0 and len([share for share in self.shares if share.company_enum == company_enum]) != 0

    def get_or_insert(self, company_enum: CompanyEnum):
        if not self.has_stock(company_enum):
            share = SharesOfCompany(company_enum, 0)
            self.shares.append(share)
            return share

        return next(share for share in self.shares if share.company_enum == company_enum)

    # TODO comment
    # TODO refactor: get rid of SharesOfCompany? do we really use that object somewhere?
    def get_by_name(self, company_enum: CompanyEnum) -> SharesOfCompany:
        """
            Returns SharesOfCompany for company name, or None if nothing found
        """
        return next((share for share in self.shares if share.company_enum == company_enum), None)

    # Return the amount of shares we hold from the given company.
    # If we don't hold any shares of this company, we return 0.
    def get_amount(self, company_enum: CompanyEnum) -> int:
        share = self.get_by_name(company_enum)
        if share is not None:
            return share.amount
        else:
            return 0

    def update(self, stock_market_data: StockMarketData, trade_action_list: TradingActionList):
        """
        Iterates through the list of trading actions (`trade_action_list`), applies those actions and returns an updated
        `Portfolio` object based on the given `StockMarketData`. If `trade_action_list` is empty nothing will be changed
        :param stock_market_data: The market data based on which the actions are applied
        :param trade_action_list: The list of trading action to apply
        :return: An updated portfolio. This is a deep copy of the given `portfolio` (see `copy.deepcopy`)
        """
        updated_portfolio = copy.deepcopy(self)

        print(f"\nUpdate portfolio {self.name}")

        if trade_action_list.is_empty():
            print("No action this time")
            return updated_portfolio

        for trade_action in trade_action_list.iterator():
            company_enum = trade_action.shares.company_enum

            current_date = stock_market_data.get_most_recent_trade_day()
            current_price = stock_market_data.get_most_recent_price(company_enum)

            print(f"Available cash on {current_date}: {updated_portfolio.cash}")
            # for share in update.shares:
            share = updated_portfolio.get_or_insert(company_enum)
            # if share.name is update.shares.name:
            amount = trade_action.shares.amount
            trade_volume = amount * current_price

            if trade_action.action is TradingActionEnum.BUY:
                print(f"  Buying {amount} shares of '{share.company_enum}' with an individual value of {current_price}")
                print(f"  Volume of this trade: {trade_volume}")

                if trade_volume <= updated_portfolio.cash:
                    share.amount += amount
                    updated_portfolio.cash -= trade_volume
                else:
                    print(f"  No sufficient cash reserve ({updated_portfolio.cash}) for planned transaction with "
                          f"volume of {trade_volume}")
            elif trade_action.action is TradingActionEnum.SELL:
                print(f"  Selling {amount} shares of {share.company_enum} with individual value of {current_price}")
                print(f"  Volume of this trade: {trade_volume}")

                if share.amount > amount:
                    share.amount -= amount
                    updated_portfolio.cash += trade_volume
                else:
                    print(f"  Not sufficient shares in portfolio ({amount}) for planned sale of {share.amount} shares")

            print(f"Resulting available cash after trade: {updated_portfolio.cash}")

            total_portfolio_value = updated_portfolio.total_value(current_date, stock_market_data.market_data)
            print(f"Total portfolio value after trade: {total_portfolio_value}")

        return updated_portfolio

    def isTradingActionListValid(self, tradingActionList: TradingActionList, stockMarketData: StockMarketData) -> bool:
        """
        Validates if generated TradingActionList is valid in comparison to current Portfolio
        Args:
          trading_action_list : TradingActionList containing generated TradingAction's to be sent into Evaluation (Stock Market)
          stockMarketData: StockMarketData containing date for all companies
        Returns:
          A True if given TradingActionList is valid in comparison to current Portfolio, False otherwise, never None
        """

        current_cash = self.cash

        most_recent_price_company_a = stockMarketData.get_most_recent_price(CompanyEnum.COMPANY_A)
        trading_action_for_company_a = tradingActionList.get_by_CompanyEnum(CompanyEnum.COMPANY_A)

        is_valid, current_cash = self.__isTradingActionValid(current_cash, CompanyEnum.COMPANY_A,
                                                             trading_action_for_company_a, most_recent_price_company_a)
        if (is_valid is False):
            return False

        most_recent_price_company_b = stockMarketData.get_most_recent_price(CompanyEnum.COMPANY_B)
        trading_action_for_company_b = tradingActionList.get_by_CompanyEnum(CompanyEnum.COMPANY_B)

        is_valid, current_cash = self.__isTradingActionValid(current_cash, CompanyEnum.COMPANY_B,
                                                             trading_action_for_company_b, most_recent_price_company_b)
        if (is_valid is False):
            return False

        return True

    def __isTradingActionValid(self, current_cash: float, company_enum: CompanyEnum, trading_action_for_company: TradingAction,
                               most_recent_price_company: float):
        """
        Validates if given TradingAction is valid
        Args:
          current_cash : TradingActionList containing generated TradingAction's to be sent into Evaluation (Stock Market)
          company_enum : CCompanyEnum
          trading_action_for_company: TradingAction
          most_recent_price_company: most recent price of company as float
        Returns:
          A True if given TradingAction is valid in comparison to current Portfolio and Cash, False otherwise, never None
        """
        if (trading_action_for_company is not None):
            if (trading_action_for_company.action == TradingActionEnum.BUY):
                price_to_pay = most_recent_price_company * trading_action_for_company.shares

                current_cash = current_cash - price_to_pay
                if (current_cash < 0):
                    # TODO: use Logging!!!
                    print(
                        f"!!!! RnnTrader - WARNING: Not enough money to pay! tradingActionForCompany: {trading_action_for_company}, Portfolio: {self}")
                    return False, current_cash

            elif (trading_action_for_company.action == TradingActionEnum.SELL):
                if (trading_action_for_company.shares > self.get_amount(company_enum)):
                    return False
            else:
                raise ValueError(f'Action for tradingActionForCompanyB is not valid: {trading_action_for_company}')

        return True, current_cash
