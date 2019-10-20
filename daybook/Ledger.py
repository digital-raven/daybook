""" Ledger and Hints class.
"""

import configparser
import csv
import os

import dateparser

from daybook.Account import Account
from daybook.Amount import Amount
from daybook.Transaction import Transaction


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

        # Detect redundant transactions.
        self.unique_transactions = dict()

    def sort(self):
        """ Sort the ledger's transactions by date.
        """
        self.transactions.sort()
        for key, val in self.accounts.items():
            val.transactions.sort()

    def dump(self):
        s = 'date,src,dest,amount,tags,notes\n'
        for t in self.transactions:
            s = s + str(t) + '\n'
        return s

    def addTransactions(self, transactions, func=lambda x: True):
        """ Add list of transactions

        There will be no reference sharing - all mutable data are copied,
        and this ledger will create its own unique account references.

        Args:
            transactions: Transactions to import.
            func: Function reference that should return True on transactions
                to import and False on those to be denied.

        Returns:
            A list containing internal references to the new transactions.
        """
        return [self.addTransaction(t) for t in transactions if func(t)]

    def load(self, csvfiles):
        """ Load ledger using from multiple CSVs.

        Args:
            csvfiles: list of csvfiles to load.

        Returns:
            A list of internal references to the new transactions.

        Raises:
            See loadCsv.
        """
        [t for f in csvfiles for t in self.loadCsv(f)]

    def loadCsv(self, csvfile):
        """ Loads transactions into this ledger from a single csv.

        If the CSV contains an invalid row, then no changes will be
        committed to the ledger, and ValueError will be raised.

        Args:
            csvfile: Path to csv containing transactions.

        Returns:
            A list containing internal references to the new transactions.

        Raises:
            FileNotFoundError: The csv wasn't found.
            PermissionError: The csv exists but could not be read.
            ValueError: A row from the CSV was invalid.
        """
        newtrans = []

        thisname = os.path.splitext(os.path.basename(csvfile))[0]
        with open(csvfile, 'r') as ifs_:
            line_num = 1
            reader = csv.DictReader(ifs_)

            # keep track of currency suggestions within this spreadsheet.
            last_currencies = {}
            for row in reader:
                try:
                    date = dateparser.parse(row['date'])

                    # will raise ValueError if invalid.
                    src = self.suggestAccount(row['src'], thisname)
                    dest = self.suggestAccount(row['dest'], thisname)

                    # determine what currencies to use and validate amount
                    suggested_src = Account.default_currency
                    suggested_dest = Account.default_currency
                    if src.name in last_currencies:
                        suggested_src = last_currencies[src.name]
                    elif src.name in self.accounts:
                        suggested_src = self.accounts[src.name].last_currency
                    if dest.name in last_currencies:
                        suggested_dest = last_currencies[dest.name]
                    elif dest.name in self.accounts:
                        suggested_dest = self.accounts[dest.name].last_currency

                    amount = Amount.createFromStr(
                        row['amount'], suggested_src, suggested_dest)

                    tags = [x for x in row['tags'].split(':') if x]
                    notes = row['notes']

                    # will raise ValueError if invalid.
                    t = Transaction(date, src, dest, amount, tags, notes)

                    # update currency suggestions
                    last_currencies[src.name] = amount.src_currency
                    last_currencies[dest.name] = amount.dest_currency
                except ValueError as ve:
                    raise ValueError(
                        'CSV {}: Line {}: {}'.format(
                            csvfile, line_num, ve))

                newtrans.append(t)
                line_num = line_num + 1

        # commit transactions to ledger. this code cannot raise.
        return self.addTransactions(newtrans)

    def addTransaction(self, t):
        """ Add a transaction to the ledger.

        The appropriate way to use this function is...

            x = self.addTransaction(x)

        Because the ledger will insert a shallow-copy of t, but this copy
        will be updated with internal account references.

        Args:
            t: Transaction object to attempt to add.

        Returns:
            A reference to the transaction object within the ledger.
        """
        if t not in self.unique_transactions:

            # create our own copy
            t = Transaction(t.date, t.src, t.dest, t.amount, t.tags, t.notes)

            # add copies of the accounts and update t.
            t.src = self.addAccount(t.src)
            t.dest = self.addAccount(t.dest)

            # commit the transaction
            self.transactions.append(t)
            t.src.addTransaction(t)
            t.dest.addTransaction(t)
            self.unique_transactions[t] = t

            return t
        else:
            internal = self.unique_transactions[t]
            internal.addTags(t.tags)
            return internal

    def suggestAccount(self, string, thisname='uncategorized'):
        """ Parse a string and create an account reference from it.

        Uses self.hints to help with account creation.

        Args:
            string: String containing account information.
            thisname: Name to use for src or dest in case they're named 'this'.

        Returns:
            New Account reference.

        Raises:
            ValueError: No valid account could be created from string.
        """

        l_ = [x for x in string.split(' ') if x]

        if l_[0] == 'this':
            l_[0] = thisname

        if l_[0] not in self.accounts:
            suggestion = self.hints.suggest(' '.join(l_))
            if suggestion:
                l_ = [suggestion]

        return Account.createFromList(l_)

    def addAccount(self, account):
        """ Add an account to this ledger.

        If an account of matching name already exists, then the tags will
        be appended, and type will be ignored.

        The way to use this function is

            x = ledger.addAccount(x)

        This is because the ledger creates a new internal reference using
        the data in x. The transactions are not moved.

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
