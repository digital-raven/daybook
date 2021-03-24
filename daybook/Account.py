""" Account classes
"""

from collections import defaultdict


class Account:
    """ An account containing transactions.

    Types dictate the behavior of the balance per transaction.

        asset => Accounts that have a positive effect on your net worth.
        expense => Accounts that track money spent on consumable goods.
        income => Track sources of income. eg. your employer.
        liability => Debts, which have a negative effect on your net worth.
        receivable => Money owed to you.
        void => Create or destroy funds.
            eg. Set a starting balance for a checking account.
    """

    types = [
        'asset',
        'expense',
        'income',
        'liability',
        'receivable',
        'void',
    ]

    def __init__(self, name):
        """ Initialize a new account instance.

        Mutable references are copied.

        Args:
            name: Dot-separated name of the account. Must contain no spaces.
                First field must be in Account.types.
        """
        if ' ' in name:
            raise ValueError('Account name "{}" must contain no spaces.'.format(name))

        fields = [x for x in name.split('.') if x]
        if not fields:
            raise ValueError('No account information specified.')

        # the type can be a prefix of any of Account.types
        type_ = fields[0]
        type_ = [x for x in Account.types if x.startswith(type_)]
        if not type_:
            raise ValueError('Account type "{}" is not in {}.'.format(fields[0], Account.types))
        self.type = type_[0]

        # put after type check for more intuitive error message.
        if len(fields) == 1:
            raise ValueError('Account "{}" contains a type, but no name.'.format(name))

        self.name = '.'.join([self.type] + fields[1:])

        # transaction references
        self.transactions = []

        # once balance per currency
        self.balances = defaultdict(lambda: 0)

        # most recent currency used in a transaction
        self.last_currency = None

    def addTransactions(self, transactions):
        """ Add transactions to this account.

        Args:
            transactions: List of transactions to add.
        """
        for t in transactions:
            self.addTransaction(t)

    def addTransaction(self, t):
        """ Update balances and append transaction.
        """
        if self not in [t.src, t.dest]:
            raise ValueError('Im not in this transaction')

        amount = t.amount
        scurr = t.amount.src_currency
        dcurr = t.amount.dest_currency

        if self is t.src:
            self.balances[scurr] = self.balances[scurr] + t.amount.src_amount
            self.last_currency = scurr
        if self is t.dest:
            self.balances[dcurr] = self.balances[dcurr] + t.amount.dest_amount
            self.last_currency = dcurr

        self.transactions.append(t)
