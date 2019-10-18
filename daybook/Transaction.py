""" Ledger, Account, and Transaction classes
"""

import copy
from datetime import datetime

from daybook.Account import Account
from daybook.Amount import Amount

class Transaction:

    def __init__(self, date, src, dest, amount, tags=None, notes=''):

        if not type(date) == datetime:
            raise ValueError('Invalid date.')

        if not type(src) == Account or not type(dest) == Account:
            raise ValueError('src and dest need to be of type Account.')

        if not type(amount) == Amount:
            raise ValueError('amount must be of type Amount')

        self.date = date
        self.src = src
        self.dest = dest
        self.amount = copy.copy(amount)
        self.tags = {x for x in tags if x} if tags else set()
        self.notes = notes

        # this key information shouln't ever be modified.
        self._hash = hash('{}{}{}{}'.format(
            self.date,
            self.src.name,
            self.dest.name,
            self.amount))

    def __lt__(self, other):
        return self.date < other.date

    def __hash__(self):
        return self._hash

    def __eq__(self, other):
        return (
            self.date == other.date
            and self.src.name == other.src.name
            and self.dest.name == other.dest.name
            and self.amount == other.amount)

    def addTags(self, tags):
        tmp = {x for x in tags if x}
        self.tags.update(tmp)
