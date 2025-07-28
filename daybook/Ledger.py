""" Ledger class and basic filter function.
"""

import csv
import io
import os

from superdate import SuperDate

from daybook.Account import Account
from daybook.Amount import Amount
from daybook.Transaction import Transaction
from daybook.util.DupeTracker import DupeTracker


def suggest_notes(src, dest, amount):
    """ Create an automatic notes suggestion.

    Uses the first 3 words of either entry. If src and dest are the
    same or weren't provided, then use the currencies as this was
    likely an exchange within the same account. This probably indicates
    a stock transfer.

    Args:
        src: 'src' line from the csv row.
        dest: 'dest' line from the csv row.
        amount: Amount object.

    Returns:
        A suggestion as a str.
    """
    src = ' '.join(src.split()[0:3]) if src else ''
    dest = ' '.join(dest.split()[0:3]) if dest else ''

    accts = [x for x in [src, dest] if x]
    currs = [amount.src_currency, amount.dest_currency] if amount else []

    return ' -> '.join(accts if src != dest else currs)


class Ledger:

    def __init__(self, primary_currency, duplicate_window=0):
        """ Init a new Ledger object.

        Args:
            primary_currency: Primary currency for the ledger.
            duplicate_window: Transactions from different perspectives
                whose dates are <= this value will be flagged as
                duplicates and not inserted. Set to False to disable
                duplicate detection.
        """

        self.primary_currency = primary_currency
        self.duplicate_window = duplicate_window

        self.accounts = {}
        self.transactions = []

        # Detect redundant transactions.
        self.dupes = DupeTracker(self.duplicate_window)

        # Number of times "addTransactions" is called.
        self.num_adds = 0

    def clear(self):
        """ Clear the ledger and start from scratch.
        """
        self.accounts = {}
        self.transactions = []
        self.dupes = DupeTracker(self.duplicate_window)
        self.num_adds = 0

    def sort(self):
        """ Sort the ledger's transactions by date.
        """
        self.transactions.sort()
        for key, val in self.accounts.items():
            val.transactions.sort()

    def dump(self, filter=lambda x: True):
        """ Dump contents of ledger as csv string.

        This function can filter for Transactions.

        Args:
            func: Function that returns True or False when
                provided with a Transaction.

        Returns:
            The leddger's content's as a CSV string.
        """
        h = ['date,src,dest,amount,tags,notes']
        body = [str(t) for t in self.getTransactions(filter)]
        return '\n'.join(h + body)

    def getTransactions(self, filter=lambda x: True):
        """ Retrieve a list of filtered transactions.

        Args:
            func: Function that returns True or False when provided
                with a Transaction.

        Returns:
            List of internal transaction references.
        """
        if type(filter) is str:
            return [t for t in self.transactions if eval(filter)]
        elif callable(filter):
            return [t for t in self.transactions if filter(t)]

    def filtered(self, filter=lambda x: True):
        """ Return a ledger consisting only of filtered transactions.

        Args:
            func: Expression to be evaluated per each transaction.

        Returns:
            A ledger loaded only with transactions that
        """
        subledger = Ledger(self.primary_currency)
        subledger.load(self.dump(filter))
        return subledger

    def reportDupes(self, transactions):
        """ Report which transactions are duplicates.

        transactions should be a list of transactions returned from
        Ledger.addTransactions or any of the load methods.

        Args:
            transactions: A list of transaction references.

        Returns:
            A list of tuples. Each contains the transaction
            reference that was inserted as a duplicate, as well as
            the perspective of the original transaction, and the
            perspective of the proivded reference.

            Example iteration through this list:

                transactions = ledger.addTransactions(transactions, 'asset.checking')
                dupes = ledger.reportDupes(transactions)
                for t, o, a in dupes:
                    print(t, o, a)
        """
        ts = transactions
        orefs, ops, aps = self.dupes.getPerspectives(ts)

        return [(t, op, ap) for oref, t, op, ap in zip(orefs, ts, ops, aps) if oref is not t]

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
        """ Load ledger from a single CSV.

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

    def load(self, lines, thisname='', hints=None, skipinvals=False):
        """ Loads transactions into this ledger from csv-lines.

        No transactions will be committed to the ledger if any line
        contains an invalid entry.

        Args:
            lines: List of lines to be added. The first line must be the
                headings 'date,src,dest,amount,tags,notes'.
            thisname: Name to use in case an account is named 'this'.
                Also serves as perspective for incoming transactions.
            hints: Hints reference to help with accont creation.
            skipinvals: Silently pass lines deemed invalid.

        Returns:
            A list containing internal references to the new transactions.

        Raises:
            ValueError: A row from the CSV was invalid.
        """
        perspective = thisname
        thisname = thisname or 'void.void'

        if type(lines) is str:
            lines = io.StringIO(lines)

        newtrans = []
        reader = csv.DictReader(lines)
        if 'date' not in reader.fieldnames:
            raise ValueError('No "date" fieldname found.')

        # keep track of currency suggestions within this spreadsheet.
        line_num = 2
        for row in reader:
            try:
                date = SuperDate(row['date'])

                notes = ''
                if 'notes' in row:
                    notes = row['notes']

                # determine src and dest accounts.
                src = None
                dest = None

                src_line = row['src'] if 'src' in row else None
                dest_line = row['dest'] if 'dest' in row else None

                # will raise ValueError if invalid.
                if src_line is not None:
                    src = self.suggestAccount(src_line, thisname, hints)

                if dest_line is not None:
                    dest = self.suggestAccount(dest_line, thisname, hints)

                src = src or self.suggestAccount('this', thisname, hints)
                dest = dest or self.suggestAccount('this', thisname, hints)

                # determine what currencies to use and validate amount
                suggestion = self.primary_currency

                try:
                    amount = Amount.createFromStr(row['amount'], suggestion)
                except KeyError:
                    amount = Amount(suggestion, 0, suggestion, 0)

                # src amount should always be negative.
                if amount.src_amount > 0:
                    src, src_line, dest, dest_line = dest, dest_line, src, src_line
                    amount.correct()

                notes = notes or suggest_notes(src_line, dest_line, amount)

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
        return self.addTransactions(newtrans, perspective)

    def addTransactions(self, transactions, perspective=''):
        """ Add list of transactions.

        There will be no reference sharing - all mutable data are copied,
        and this ledger will create its own unique account references.

        The list returned by this function can be examined for duplicate
        transactions by passing it to Ledger.reportDupes.

        Args:
            transactions: Transactions to import.
            perspective: See Ledger.addTransaction.

        Returns:
            A list containing internal references to the new transactions.
        """
        self.num_adds += 1
        return [self.addTransaction(t, perspective, self.num_adds) for t in transactions]

    def addTransaction(self, t, perspective='', block=0):
        """ Add a transaction to the ledger.

        The appropriate way to use this function is...

            x = self.addTransaction(x)

        Because the ledger will insert a shallow-copy of t, but this copy
        will be updated with internal account references.

        A transaction will only be committed if is not a duplicate. If a
        transaction is within a few days of another, very similar,
        transaction (identical src and dest accounts and identical amounts),
        but of a differing perspective, then daybook will assume that two or
        more sources are reporting on the same event. This transaction is then
        flagged as a duplicate and is not committed.

        If a transaction is a duplicate, then the reference returned by this
        function will corrsepond to a "True" output from Ledger.reportDupes.

        Args:
            t: Transaction object to attempt to add.
            perspective: The perspective from which these transactions are
                being reported. This is likely the base name of the CSV
                that reported the transactions.
            block: Block ID of the transaction. If a transaction with a
                perspective of '' is added and there exists an identical
                transaction with a perspective of '' but was inserted with
                a lower block number, then the current transaction is
                not inserted, the block number of the existing transaction
                is updated, and a reference to the existing transaction
                is returned.

        Returns:
            A reference to the transaction object within the ledger.
        """

        # create our own copy
        src = self.addAccount(t.src)
        dest = self.addAccount(t.dest)
        t = Transaction(t.date, src, dest, t.amount, t.tags, t.notes)

        orig, t = self.dupes.checkDupe(t, perspective, block)
        if orig is not None:
            orig.addTags(t.tags)
        else:
            self.transactions.append(t)
            t.src.addTransaction(t)
            if t.src is not t.dest:
                t.dest.addTransaction(t)

        return t

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
