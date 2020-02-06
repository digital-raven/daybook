""" Ledger and Hints class.
"""

import configparser
import csv
import io
import os
import string

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


class Hints:
    def __init__(self, hints=''):
        """ Constructor for Hints class.

        Args:
            hints: Path to the hints file.
        """
        self.hints = {}
        if hints:
            self.load(hints)

    def _loadColonConf(self, conf):
        """ Load a colonconf as a dict.

        A colonconf is a simple conf file format where the variable names
        are allowed to contain anything, but the reason for creating this
        was to permit colons in the names.

        Some entries might look like this.

            simplevar=4
            my:var:name = line1
                line2

            multi:line2 =
                first
                second

        And the associated dict will contain the following. All keys and
        values are str type.

            {'simplevar':'4',
             'my:var:name':'line1\nline2',
             'multi:line2':'first\nsecond'}

        Values extending multiple lines require at least one preceeding
        whitespace character on the additional lines.

        Line comments are supported as well. The line must begin with a '#'
        and have no preceeding white-space.

        Args:
            conf: Path to the colon conf.

        Returns:
            A dictionary where the keys are the vars read from the file
            and the values are the associated strings.

        Raises:
            FileNotFoundError or PermissionError if the file could not
            be opened.
        """
        curvar = None
        d = {}
        s = ''

        with open(conf) as f:
            s = f.read()

        for l_ in s.splitlines():
            if l_[0:1] not in string.whitespace:
                # skip comment lines
                if '#' == l_.strip()[0:1]:
                    continue

                # else beginning of a new variable declaration.
                l_ = l_.split('=')
                curvar = l_[0].strip()
                d[curvar] = ['='.join(l_[1:]).strip()]
            else:
                # keep adding to current variable
                if curvar in d:
                    d[curvar].append(l_.strip())

        return {k: '\n'.join(v).strip() for (k, v) in d.items()}

    def load(self, hints):
        """ Load additional entries from a hints file.

        Args:
            hints: path to the hints file.

        Raises:
            FileNotFoundError or PermissionError if the file
            couldn't be opened.
        """
        d = self._loadColonConf(hints)

        for key, value in d.items():
            lines = [x for x in value.splitlines() if x]
            for line in lines:
                self.hints[line] = key

    def suggest(self, s):
        """ Suggest an entry given a string.

        Args:
            s: The string to search for within self.hints.

        Returns:
            If s is an exact match, then that value is returned. If not, then
            self.hints is searched for a key which contains s. If one is found,
            then that value is returned. First-come only-served.
        """
        if s in self.hints:
            return self.hints[s]

        for key, value in self.hints.items():
            if key in s:
                return value

        return ''


class Ledger:

    def __init__(self, primary_currency, hints=None):

        if isinstance(hints, Hints):
            self.hints = hints
        else:
            self.hints = Hints(hints)

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
        self.hints = Hints()
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

    def loadCsvs(self, csvfiles):
        """ Load ledger from multiple CSVs.

        Args:
            csvfiles: list of csv filename to load from.

        Returns:
            A list of internal references to the new transactions.

        Raises:
            See loadCsv.
        """
        return [t for f in csvfiles for t in self.loadCsv(f)]

    def loadCsv(self, csvfile):
        thisname = os.path.splitext(os.path.basename(csvfile))[0]
        with open(csvfile, 'r') as f:
            try:
                return self.load(f, thisname)
            except ValueError as ve:
                raise ValueError('CSV {}: {}'.format(csvfile, ve))

    def load(self, lines, thisname='this'):
        """ Loads transactions into this ledger from csv-lines.

        No transactions will be committed to the ledger if any line
        contains an invalid entry.

        Args:
            lines: List of lines to be added. The first line must be the
                headings 'date,src,dest,amount,tags,notes'.

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
                    src = self.suggestAccount(row['src'], thisname)

                if 'dest' in row:
                    dest = self.suggestAccount(row['dest'], thisname)

                if (not src or not dest) and 'target' in row:
                    target = self.suggestAccount(row['target'], thisname)
                    notes = notes or row['target']

                    if src:
                        dest = target
                    elif dest:
                        src = target
                    else:
                        # determine src and dest based on sign of first num.
                        try:
                            tmpamount = get_nums(row['amount'])[0]
                        except IndexError:
                            raise ValueError('No quantities in "amount" field')

                        if tmpamount < 0:
                            src = self.suggestAccount('this', thisname)
                            dest = target
                        else:
                            src = target
                            dest = self.suggestAccount('this', thisname)

                src = src or self.suggestAccount('this', thisname)
                dest = dest or self.suggestAccount('this', thisname)

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

                amount = Amount.createFromStr(
                    row['amount'], suggested_src, suggested_dest)

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
        if t not in self.unique_transactions:

            # create our own copy
            t = Transaction(t.date, t.src, t.dest, t.amount, t.tags, t.notes)

            # add copies of the accounts and update t.
            t.src = self.addAccount(t.src)
            t.dest = self.addAccount(t.dest)

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

    def suggestAccount(self, s, thisname='uncategorized'):
        """ Parse a string and create an account reference from it.

        Uses self.hints to help with account creation.

        Args:
            s: String from which a suggestion will be made.
            thisname: Name to use for src or dest in case they're named 'this'.

        Returns:
            New Account reference.

        Raises:
            ValueError: No valid account could be created from s.
        """
        s = s or 'void'

        l_ = [x for x in s.split(' ') if x]

        if l_[0] == 'this':
            l_[0] = thisname

        if l_[0] not in self.accounts:
            suggestion = self.hints.suggest(s)
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
