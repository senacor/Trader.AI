from model.CompanyEnum import CompanyEnum


class SharesOfCompany:
    """
    Represents number of owned shares of one type (company)
    """

    def __init__(self, company_enum: CompanyEnum, amount: int):
        """
        Constructor

        Args:
          company_enum: CompanyEnum
          amount: amount of shares
        """
        self.company_enum = company_enum
        self.amount = amount

    def __repr__(self) -> str:
        return f"<SharesOfCompany(company_enum={self.company_enum}, amount={self.amount})>"
