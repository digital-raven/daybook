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
    }

    def __init__(self, name='', type_='asset', tags=None):
        """ Initialize a new account instance.

        Mutable references are copied.

        Args:
            name: Name of the account. Must contain no spaces.
            type: Type of account. Must be in Account.types.
            tags: Container of tags for account. The account will
                create a unique set internally.
        """

        if type_ not in Account.types:
            raise ValueError('Account type must be in {}.'.format(
                Account.types))

        if ' ' in name:
            raise ValueError('Account names may not contain spaces.')

        self.name = name
        self.type = type_
        self.tags = {x for x in tags if x} if tags else set()

        # transaction references
        self.transactions = []

        # once balance per currency
        self.balances = defaultdict(lambda: 0)

        # most recent currency used in a transaction
        self.last_currency = None

    def addTags(self, tags):
        tmp = {x for x in tags if x}
        self.tags.update(tmp)

    def addTransactions(self, transactions):
        """ Add transactions to this account

        The account will only add transasctions that include this account.

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
            self.balances[scurr] = self.balances[scurr] - t.amount.src_amount
            self.last_currency = scurr
        if self is t.dest:
            self.balances[dcurr] = self.balances[dcurr] + t.amount.dest_amount
            self.last_currency = dcurr

        self.transactions.append(t)

    @classmethod
    def createFromList(cls, l_):
        """ Parse a list to create a new account.

            This list can match the following format...

                name [type] [tag1[:tag2]]

            If type is provided alongside tags, then type must come first.
            Tags must be separated by colon

        Args:
            l_: The list containing Account information.

        Returns:
            A new Account.

        Raises:
            ValueError if the len was not in 1, 2, or 3, or if
            the value read from the 'type' field was invalid.
        """

        name = ''
        type_ = 'asset'
        tags = []

        if len(l_) == 1:
            name = l_[0]
        elif len(l_) == 2:
            name = l_[0]
            if l_[1] in Account.types:
                type_ = l_[1]
            else:
                tags = l_[1].split(':')
        elif len(l_) == 3:
            name = l_[0]
            type_ = l_[1]
            tags = [x for x in l_[2].split(':') if x]
        else:
            raise ValueError(
                'Accounts must be created with 1, 2, or 3 '
                'space-separated fields.')

        return Account(name, type_, tags)
