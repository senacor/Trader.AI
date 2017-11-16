class SharesOfCompany:
    '''
    Represents number of owned shares of one type (company)
    '''

    def __init__(self, name: str, amount: int):
        """ Constructor

        Args:
          name : name of company
          amount : amount of shares
        """
        self.name = name
        self.amount = amount
