""" Account classes
"""

from collections import defaultdict


class Account:
    """ An account containing transactions.

    Types dictate the behavior of the balance per transaction.

        asset => Accounts that have a positive effect on your net worth.
        expense => Accounts that track money spent on consumable goods.
        income => Track sources of income. eg. your employer.
        investment => Use this for brokerage accounts.
        liability => Debts, which have a negative effect on your net worth.
        receivable => Money owed to you.
    """

    types = {
        'asset',
        'expense',
        'income',
        'investment',
        'liability',
        'receivable',
        'void',
    }

    def __init__(self, name, type_):
        """ Initialize a new account instance.

        Mutable references are copied.

        Args:
            name: Name of the account. Must contain no spaces.
            type: Type of account. Must be in Account.types.
        """

        if type_ not in Account.types:
            raise ValueError('Account type must be one of {}.'.format(
                Account.types))

        if ' ' in name:
            raise ValueError('Account names may not contain spaces.')

        if not name:
            raise ValueError('Account name may not be empty.')

        self.name = name
        self.type = type_

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

    @classmethod
    def createFromStr(cls, s):
        """ Parse a str to create a new account.

        Args:
            s: The string containing Account information.

        Returns:
            A new Account.

        Raises:
            ValueError if a valid account could not be created.
        """
        s = s.strip()
        if not s:
            raise ValueError('No account information specified.')

        l_ = [x.strip() for x in s.split('.') if x.strip()]

        type_ = ''
        name = ''

        if not l_:
            raise ValueError('No account information specified.')
        elif len(l_) == 1:
            type_ = 'void'
            name = l_[0]
        else:
            if l_[0] in Account.types:
                type_ = l_[0]
                name = '.'.join(l_[1:])
            else:
                type_ = 'void'
                name = '.'.join(l_)

        return Account(name, type_)
