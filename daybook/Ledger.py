#!/usr/bin/env python3
""" Ledger, Account, and Transaction classes
"""

import configparser
import csv
import os
from datetime import datetime

import dateparser


class Transaction:

    def __init__(self, date, src, dest, amount, tags=None, notes=''):
        if not type(date) == datetime:
            date = dateparser.parse(date)

        if not type(src) == Account or not type(dest) == Account:
            raise ValueError('src and dest need to be of type Account.')

        if type(amount) not in [float, int]:
            raise ValueError('Amount must be numeric')

        self.date = date
        self.src = src
        self.dest = dest
        self.amount = amount
        self.tags = {x for x in tags if x} if tags else set()
        self.notes = notes

    def addTags(self, tags):
        tmp = {x for x in tags if x}
        self.tags.update(tmp)

    def __str__(self):
        return ','.join([
            self.date.strftime('%Y-%m-%d %H:%M:%S'),
            self.src.name,
            self.dest.name,
            str(self.amount),
            ':'.join(self.tags),
            '"{}"'.format(self.notes)])

    def __lt__(self, other):
        """ For sorting in date order.
        """
        return self.date < other.date

    def __hash__(self):
        return hash('{} {} {} {}'.format(
            self.date,
            self.src.name,
            self.dest.name,
            self.amount))

    def __eq__(self, other):
        return self.date == other.date \
            and self.src.name == other.src.name \
            and self.dest.name == other.dest.name \
            and self.amount == other.amount


class Account:
    """ An account containing transactions.

    Types dictate the behavior of the balance per transaction.

        asset => Accounts that have a positive effect on your net worth.
        liability => Debts, which have a negative effect on your net worth.
        income => Track sources of income. eg. your employer.
        expense => Accounts that track money spent on consumable goods.
        receivable => Money owed to you.
    """

    types = {'asset', 'liability', 'income', 'expense', 'receivable'}

    def __init__(self, name='', type='asset', tags=None):

        if type not in Account.types:
            raise ValueError('type must be in {}'.format(Account.types))

        if ' ' in name:
            raise ValueError('Account names may not contain spaces.')

        self.name = name
        self.type = type
        self.tags = {x for x in tags if x} if tags else {}
        self.transactions = []

    def addTags(self, tags):
        tmp = {x for x in tags if x}
        self.tags.update(tmp)

    def addTransactions(self, transactions):
        """ Add transactions to this account

        The account will only add transasctions that include this account.

        Args:
            transactions: List of transactions to add.
        """
        t = transactions
        self.transactions.extend([x for x in t if self in [x.src, x.dest]])

    def addTransaction(self, trans):
        """ Add a transaction to this account
        """
        if self not in [trans.src, trans.dest]:
            raise ValueError

        self.transactions.append(trans)

    def balance(self, start=None, end=None):
        """ Return balance of account.

        Args:
            start: datetime representing earliest transactions to use.
            end: datetime representing upper boundry.

        Returns:
            The balance of the account as computed by transactions between
            start and end.
        """

        balance = 0
        for trans in self.transactions:
            if (not start and not end
                    or start and end and start <= trans.date <= end
                    or start and start <= trans.date
                    or end and trans.date <= end):

                if self is trans.src:
                    balance = balance - trans.amount
                if self is trans.dest:
                    balance = balance + trans.amount

        return balance

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
        type = 'asset'
        tags = []

        if len(l_) == 1:
            name = l_[0]
        elif len(l_) == 2:
            name = l_[0]
            if l_[1] in Account.types:
                type = l_[1]
            else:
                tags = l_[1].split(':')
        elif len(l_) == 3:
            name = l_[0]
            type = l_[1]
            tags = [x for x in l_[2].split(':') if x]
        else:
            raise ValueError

        return Account(name, type, tags)


class Hints:
    def __init__(self, hintsini=''):
        self.hints = {}
        if hintsini:
            self.load(hintsini)

    def load(self, hintsini):
        """ Add hints from a hints.ini

        Accepts a path to an ini where each entry is an account name. Each line
        indicates a name that, if found within a transaction's src, or dest
        fields, belongs to that transaction.

        Args:
            hintsini: Path to hints ini.

        Raises:
            FileNotFoundError or PermissionError if the hints.ini could not
            be opened.
        """
        c = configparser.ConfigParser()

        # confparser.read doesn't error on file-not-found or bad permissions.
        stream = open(hintsini, 'r')
        stream.close()

        c.read(hintsini)

        if 'hints' not in c:
            return

        for key, value in c['hints'].items():
            lines = [x for x in value.splitlines() if x]
            for line in lines:
                self.hints[line] = key

    def suggest(self, string):
        if string in self.hints:
            return self.hints[string]

        for key, value in self.hints.items():
            if key in string:
                return value

        return ''


class Ledger:

    def __init__(self, hints=None, hintsini=''):
        if not hints:
            hints = Hints(hintsini)

        self.accounts = {}
        self.transactions = []
        self.hints = hints

        # key - date of transaction
        # hash created from transaction's src.name, dest.name, and amount.
        self._buckets = {}

    def sort(self):
        """ Sort the ledger's transactions by date.
        """
        self.transactions.sort()
        for key, val in self.accounts.items():
            val.transactions.sort()

    def load(self, csvfiles):
        """ Load ledger using from multiple CSVs.

        Args:
            csvfiles: list of csvfiles to load.
        """
        for f in csvfiles:
            self.loadCsv(f)

    def loadCsv(self, csvfile):
        """ Loads transactions into this ledger from a single csv.

        Args:
            csvfile: Path to csv containing transactions.
        """
        thisname = os.path.splitext(os.path.basename(csvfile))[0]
        with open(csvfile, 'r') as ifs_:
            reader = csv.DictReader(ifs_)
            for row in reader:
                self.addTransaction(row, thisname)

    def addTransaction(self, row, thisname='uncategorized'):
        """ Add a transaction from the data in row.

        Args:
            row: dict with fields for name, src, dest, amount, tags, notes.
            thisname: determine what account the transaction should be labeled
                as in case of 'this'.

        Returns:
            Transaction object.
        """
        date = row['date']
        src = self.suggestAccount(row['src'], thisname)
        dest = self.suggestAccount(row['dest'], thisname)
        amount = float(row['amount'])
        tags = [x for x in row['tags'].split(':') if x]
        notes = row['notes']

        src = self.addAccount(src)
        dest = self.addAccount(dest)

        t = Transaction(date, src, dest, amount, tags, notes)

        if t.date not in self._buckets:
            self._buckets[t.date] = {}

        # if this transaction already exists, add the tags from this entry
        # and return.
        if t not in self._buckets[t.date]:
            self._buckets[t.date][t] = t
        else:
            self._buckets[t.date][t].addTags(t.tags)
            return

        self.transactions.append(t)
        src.addTransaction(t)
        dest.addTransaction(t)

    def suggestAccount(self, string, thisname='uncategorized'):
        """ Parse a string and create an account reference from it.

        Uses self.hints to help with account creation.

        Args:
            string: String containing account information.
            thisname: Name to use for src or dest in case they're named 'this'.

        Returns:
            New Account reference.
        """

        l_ = [x for x in string.split(' ') if x]

        if l_[0] == 'this':
            l_[0] = thisname

        if l_[0] not in self.accounts:
            suggestion = self.hints.suggest(' '.join(l_))
            if suggestion:
                l_ = [suggestion]

        try:
            return Account.createFromList(l_)
        except ValueError:
            return Account(name='uncategorized')

    def addAccount(self, account):
        """ Add an account to this ledger.

        If an account of matching name already exists, then the tags will
        be appended, and type will be ignored.

        The way to use this function is

            x = ledger.addAccount(x)

        This is because x is reassigned to the reference
        within the ledger. The transactions are not moved.

        Args:
            account: Account to add.

        Returns:
            A reference to the account added/modified within this ledger.
        """

        if account.name in self.accounts:
            self.accounts[account.name].addTags(account.tags)
        else:
            self.accounts[account.name] = Account(
                account.name,
                account.type,
                account.tags)

        return self.accounts[account.name]
