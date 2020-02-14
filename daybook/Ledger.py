""" Ledger class.
"""

import csv
import io
import os

import dateparser

from daybook.Account import Account
from daybook.Amount import Amount
from daybook.Transaction import Transaction


def get_nums(s):
    """ Returns list of nums found within a string.
    """
    s = s.replace(':', ' ').split()
    nums = []
    for tok in s:
        try:
            nums.append(float(tok))
        except ValueError:
            pass
    return nums


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

    def loadCsvs(self, csvfiles, hints=None):
        """ Load ledger from multiple CSVs.

        Args:
            csvfiles: list of csv filename to load from.

        Returns:
            A list of internal references to the new transactions.

        Raises:
            See loadCsv.
        """
        return [t for f in csvfiles for t in self.loadCsv(f, hints)]

    def loadCsv(self, csvfile, hints=None):
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
                return self.load(f, thisname, hints)
            except ValueError as ve:
                raise ValueError('CSV {}: {}'.format(csvfile, ve))

    def load(self, lines, thisname='this', hints=None):
        """ Loads transactions into this ledger from csv-lines.

        No transactions will be committed to the ledger if any line
        contains an invalid entry.

        Args:
            lines: List of lines to be added. The first line must be the
                headings 'date,src,dest,amount,tags,notes'.
            thisname: Name to use in case an account is named 'this'.
            hints: Hints reference to help with accont creation.

        Returns:
            A list containing internal references to the new transactions.

        Raises:
            FileNotFoundError: The csv wasn't found.
            PermissionError: The csv exists but could not be read.
            ValueError: A row from the CSV was invalid.
        """
        if type(lines) == str:
            lines = io.StringIO(lines)

        newtrans = []
        reader = csv.DictReader(lines)

        # keep track of currency suggestions within this spreadsheet.
        last_currencies = {}
        line_num = 2
        for row in reader:
            try:
                date = dateparser.parse(row['date'])

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

                if (not src or not dest) and 'target' in row:
                    target = self.suggestAccount(row['target'], thisname, hints)
                    notes = notes or row['target']

                    if src:
                        dest = target
                    elif dest:
                        src = target
                    else:
                        # determine src and dest based on sign of first num.
                        try:
                            tmpamount = get_nums(row['amount'])[0]
                        except KeyError:
                            tmpamount = 0
                        except IndexError:
                            raise ValueError('No quantities in "amount" field')

                        if tmpamount <= 0:
                            src = self.suggestAccount('this', thisname, hints)
                            dest = target
                        else:
                            src = target
                            dest = self.suggestAccount('this', thisname, hints)

                src = src or self.suggestAccount('this', thisname, hints)
                dest = dest or self.suggestAccount('this', thisname, hints)

                # determine what currencies to use and validate amount
                suggested_src = ''
                suggested_dest = ''
                if src.name in last_currencies:
                    suggested_src = last_currencies[src.name]
                elif src.name in self.accounts:
                    suggested_src = self.accounts[src.name].last_currency
                else:
                    suggested_src = self.primary_currency

                if dest.name in last_currencies:
                    suggested_dest = last_currencies[dest.name]
                elif dest.name in self.accounts:
                    suggested_dest = self.accounts[dest.name].last_currency
                else:
                    suggested_dest = self.primary_currency

                try:
                    amount = Amount.createFromStr(
                        row['amount'], suggested_src, suggested_dest)
                except KeyError:
                    amount = Amount(suggested_src, 0, suggested_dest, 0)

                tags = []
                if 'tags' in row:
                    tags = [x for x in row['tags'].split(':') if x]

                # will raise ValueError if invalid.
                t = Transaction(date, src, dest, amount, tags, notes)

                # update currency suggestions
                last_currencies[src.name] = amount.src_currency
                last_currencies[dest.name] = amount.dest_currency
            except ValueError as ve:
                raise ValueError('Line {}: {}'.format(line_num, ve))
            except KeyError:
                raise ValueError('Line {}: Does not contain expected fields.'.format(line_num))

            newtrans.append(t)
            line_num = line_num + 1

        # commit transactions to ledger. this code cannot raise.
        return self.addTransactions(newtrans)

    def addTransactions(self, transactions):
        """ Add list of transactions

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

    def suggestAccount(self, s, thisname='uncategorized', hints=None):
        """ Parse a string and create an account reference from it.

        Args:
            s: String from which a suggestion will be made.
            thisname: Name to use for src or dest in case they're named 'this'.
            hints: Hints reference to help with account creation.

        Returns:
            New Account reference.

        Raises:
            ValueError: No valid account could be created from s.
        """
        s = s.strip() or 'void.void'
        account = None

        try:
            account = Account.createFromStr(s)
        except ValueError:
            if hints:
                suggestion = hints.suggest(s)
                if not suggestion:
                    raise ValueError('No suggestion for "{}"'.format(s))

                try:
                    account = Account.createFromStr(suggestion)
                    return account
                except ValueError as ve:
                    raise ValueError(
                        '"{}" generated the suggestion "{}", '
                        'which is invalid: {}.'.format(s, suggestion, ve))
            else:
                raise

        if account.name == 'this':
            account.name = thisname

        if hints and account.name not in self.accounts:
            suggestion = hints.suggest(account.name)
            if suggestion:
                account = Account.createFromStr(suggestion)

        return account

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
            if self.accounts[account.name].type == 'void':
                self.accounts[account.name].type = account.type

        else:
            self.accounts[account.name] = Account(account.name, account.type)

        return self.accounts[account.name]
