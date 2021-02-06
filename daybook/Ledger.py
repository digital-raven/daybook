""" Ledger class and basic filter function.
"""

import csv
import io
import os

import dateutil.parser

from daybook.Account import Account
from daybook.Amount import Amount
from daybook.Transaction import Transaction


def in_start(start, t):
    return not start or start <= t.date


def in_end(end, t):
    return not end or t.date <= end


def in_accounts(accounts, t):
    return not accounts or t.src.name in accounts or t.dest.name in accounts


def in_currencies(currencies, t):
    expected = [t.amount.src_currency, t.amount.dest_currency]
    return not currencies or any([e in currencies for e in expected])


def in_types(types, t):
    return not types or t.src.type in types or t.dest.type in types


def in_tags(tags, t):
    return not tags or len(tags.intersection(t.tags)) > 0


def basic_filter(t, start, end, accounts, currencies, types, tags):
    """ Return True if transaction matches the criterion.

    Arguments that are None are treated as dont-cares.

    Use like this to utilize a basic filtering functionality on ledger dumps.

        ledger.dump(lambda x: basic_filter(x, start, end...))

    Args:
        t: The Transaction to test.
        start: Reject if t.date is earlier than this datetime.
        end: Reject if t.date is later than this datetime.
        accounts: Reject if t.src and t.dest are not in this
            list of account times.
        types: Reject t if neither involved account's type is in this
            list of Account types.
        tags: Reject t if none of its tags are in this list.
    """
    return (
        in_start(start, t)
        and in_end(end, t)
        and in_accounts(accounts, t)
        and in_currencies(currencies, t)
        and in_types(types, t)
        and in_tags(tags, t))


class Ledger:

    def __init__(self, primary_currency):

        self.primary_currency = primary_currency
        self.accounts = {}
        self.transactions = []

        # Detect redundant transactions.
        self.unique_transactions = dict()

    def clear(self):
        """ Clear the ledger and start from scratch.
        """
        self.accounts = {}
        self.transactions = []
        self.unique_transactions = dict()

    def sort(self):
        """ Sort the ledger's transactions by date.
        """
        self.transactions.sort()
        for key, val in self.accounts.items():
            val.transactions.sort()

    def dump(self, func=lambda x: True):
        """ Dump contents of ledger as csv string.

        This function can filter for Transactions.

        Args:
            func: Function that returns True or False when
                provided with a Transaction.

        Returns:
            The leddger's content's as a CSV string.
        """
        h = ['date,src,dest,amount,tags,notes']
        return '\n'.join(h + [str(t) for t in self.getTransactions(func)])

    def getTransactions(self, func=lambda x: True):
        """ Retrieve a list of filtered transactions.

        Args:
            func: Function that returns True or False when provided
                with a Transaction.

        Returns:
            List of internal transaction references.
        """
        return [t for t in self.transactions if func(t)]

    def filtered(self, func=lambda x: True):
        """ Return a ledger consisting only of filtered transactions.

        Args:
            func: Function that returns True or False when provided
                with a Transaction.

        Returns:
            A ledger loaded only with transactions that
        """
        subledger = Ledger(self.primary_currency)
        subledger.load(self.dump(func))
        return subledger

    def loadCsvs(self, csvfiles, hints=None, skipinvals=False):
        """ Load ledger from multiple CSVs.

        Args:
            csvfiles: list of csv filename to load from.

        Returns:
            A list of internal references to the new transactions.

        Raises:
            See loadCsv.
        """
        return [t for f in csvfiles for t in self.loadCsv(f, hints, skipinvals)]

    def loadCsv(self, csvfile, hints=None, skipinvals=False):
        """ Load ledger from a sincle CSV.

        Args:
            csvfile: csv file to load from.

        Returns:
            A list of internal references to the new transactions.

        Raises:
            ValueError and the CSV name and line number will indicate
            where the error ocurred.
        """
        thisname = os.path.splitext(os.path.basename(csvfile))[0]
        with open(csvfile, 'r') as f:
            try:
                return self.load(f, thisname, hints, skipinvals)
            except ValueError as ve:
                raise ValueError('CSV {}: {}'.format(csvfile, ve))

    def load(self, lines, thisname='void.void', hints=None, skipinvals=False):
        """ Loads transactions into this ledger from csv-lines.

        No transactions will be committed to the ledger if any line
        contains an invalid entry.

        Args:
            lines: List of lines to be added. The first line must be the
                headings 'date,src,dest,amount,tags,notes'.
            thisname: Name to use in case an account is named 'this'.
            hints: Hints reference to help with accont creation.
            skipinvals: Silently pass lines deemed invalid.

        Returns:
            A list containing internal references to the new transactions.

        Raises:
            ValueError: A row from the CSV was invalid.
        """
        if type(lines) == str:
            lines = io.StringIO(lines)

        newtrans = []
        reader = csv.DictReader(lines)
        if 'date' not in reader.fieldnames:
            raise ValueError('No "date" fieldname found.')

        # keep track of currency suggestions within this spreadsheet.
        line_num = 2
        for row in reader:
            try:
                date = dateutil.parser.parse(row['date'])

                notes = ''
                if 'notes' in row:
                    notes = row['notes']

                # determine src and dest accounts.
                src = None
                dest = None

                # will raise ValueError if invalid.
                if 'src' in row:
                    src = self.suggestAccount(row['src'], thisname, hints)

                if 'dest' in row:
                    dest = self.suggestAccount(row['dest'], thisname, hints)

                src = src or self.suggestAccount('this', thisname, hints)
                dest = dest or self.suggestAccount('this', thisname, hints)

                # determine what currencies to use and validate amount
                suggestion = self.primary_currency

                try:
                    amount = Amount.createFromStr(row['amount'], suggestion)
                except KeyError:
                    amount = Amount(suggestion, 0, suggestion, 0)

                tags = set()
                if 'tags' in row and row['tags']:
                    tags = {x.strip() for x in row['tags'].split(':') if x.strip()}

                # will raise ValueError if invalid.
                t = Transaction(date, src, dest, amount, tags, notes)

            except ValueError as ve:
                if skipinvals:
                    continue

                raise ValueError('Line {}: {}'.format(line_num, ve))

            newtrans.append(t)
            line_num = line_num + 1

        # commit transactions to ledger. this code cannot raise.
        return self.addTransactions(newtrans)

    def addTransactions(self, transactions):
        """ Add list of transactions.

        There will be no reference sharing - all mutable data are copied,
        and this ledger will create its own unique account references.

        Args:
            transactions: Transactions to import.

        Returns:
            A list containing internal references to the new transactions.
        """
        return [self.addTransaction(t) for t in transactions]

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

        # add copies of the accounts and update t.
        t.src = self.addAccount(t.src)
        t.dest = self.addAccount(t.dest)

        if t not in self.unique_transactions:

            # create our own copy
            t = Transaction(t.date, t.src, t.dest, t.amount, t.tags, t.notes)

            # commit the transaction
            self.transactions.append(t)
            t.src.addTransaction(t)
            if t.src is not t.dest:
                t.dest.addTransaction(t)
            self.unique_transactions[t] = t

            return t
        else:
            internal = self.unique_transactions[t]
            internal.addTags(t.tags)
            return internal

    def suggestAccount(self, s, thisname='void.void', hints=None):
        """ Parse a string and create an account reference from it.

        Args:
            s: String from which a suggestion will be made.
            thisname: Name to use for account in case it's named 'this'.
            hints: Hints reference to help with account creation.

        Returns:
            New Account reference.

        Raises:
            ValueError: No valid account could be created from s.
        """
        s = s.strip()
        s = thisname if s == 'this' else s
        s = 'void.void' if s == 'void' else s

        try:
            return Account(s)
        except ValueError as ve:

            if not hints:
                raise

            suggestion = hints.suggest(s)
            if not suggestion:
                raise ValueError('No suggestion for "{}".'.format(s))

            try:
                return Account(suggestion)
            except ValueError as ve:
                raise ValueError(
                    '"{}" generated the suggestion "{}", '
                    'which is invalid: {}.'.format(s, suggestion, ve))

    def addAccount(self, account):
        """ Add an account to this ledger.

        This function returns an internal reference to the account.
        The proper way to call this function is...

            x = ledger.addAccount(x)

        Args:
            account: Account to add.

        Returns:
            A reference to the account added/modified within this ledger.
        """
        if account.name not in self.accounts:
            self.accounts[account.name] = Account(account.name)

        return self.accounts[account.name]
