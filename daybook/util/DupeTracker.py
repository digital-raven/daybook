""" Classes to determine duplicate transactions.
"""

from collections import defaultdict, OrderedDict
from datetime import timedelta


class _DupeGroup:
    def __init__(self):
        self.orig = None  # Save first transaction entered.
        self.dates = set()  # Should contain 2 entries at most.
        self.transactions = OrderedDict()  # Keyed by perspective.
        self.block = 0

        # If the original transaction was empty persepctive, then this
        # holds a duplicate empty perspective.
        self.second_empty = None

    def should_own(self, transaction, perspective, window, block):
        """ Check if a transaction should be a member of this group.

        Args:
            transaction: Transaction to check.
            perspective: Perspective of the transaction.
            window: Time range in days to check dates. Set to False to
                never accept duplicates.
            block: Block id of the transaction.

        Returns:
            Returns True if transaction should belong to this group,
            False otherwise.
        """
        if window is False:
            return False

        t = transaction

        if perspective == '':
            if t.date != self.orig.date:
                return False
            elif '' not in self.transactions:
                return True
            elif '' in self.transactions and block > self.block:
                return True
            else:
                return False

        if perspective in self.transactions:
            return False

        in_range = abs(t.date - self.orig.date) <= timedelta(days=window)

        return t.date in self.dates or (len(self.dates) == 1 and in_range)

    def add(self, transaction, perspective, block):
        """ Add a transaction to this group.

        Always check the output of should_own before using this.

        Args:
            transaction: Transaction to add.
            perspective: Perspective of the transaction.
            block: Block ID of the transaction.

        Returns:
            A pair of references to what should be considered the "original"
            transaction and a reference to the inserted transaction.
        """
        t = transaction
        old_orig = self.orig

        if perspective == '':
            self.block = block
            if '' in self.transactions:
                if self.transactions[''] is self.orig:
                    self.second_empty = self.second_empty or t
                    t = self.second_empty
                else:
                    t = self.transactions['']

                return old_orig, t

        self.transactions[perspective] = t
        self.dates.add(t.date)

        self.orig = self.orig or t

        return old_orig, t

    def find_perspectives(self, transaction):
        """ Return the perspectives of a transaction reference.

        The original perspective and the perspective of the provided
        reference are returned. If the provided reference is not in
        self.transactions, then (None, None) is returned.

        Args:
            transaction: Transaction reference within this structure.

        Returns:
            The original and actual perspectives of the reference.
        """
        p_orig = list(self.transactions.keys())[0]

        if transaction is self.second_empty:
            return p_orig, ''

        for p, t in self.transactions.items():
            if t is transaction:
                return p_orig, p

        return None, None


class DupeTracker:
    """ Track duplicate transactions.
    """
    def __init__(self, window):
        self.window = window

        # Each bucket contains a list of Groups.
        self.buckets = defaultdict(list)

    def checkDupe(self, transaction, perspective, block):
        """ Determine if a transaction is a duplicate.

        The following is an example usage of this function.

            dupes = DupeTracker(5)  # arbitrary window length.
            orig, t = dupes.checkDupe(t, '', 5)
            if orig is None:
                print('t is not a duplicate')
            else:
                print('t is a duplicate of orig')

        Args:
            transaction: The transaction to test for duplication. This
                transaction will be entered into the structure.
            perspective: Perspective of the transaction.
            block: The block id of the transaction. Used only if
                perspective is ''.

        Returns:
            A pair of references to transactions within the
            structure; orig and t. If t is determined to be unique,
            then orig will be None.
        """
        t = transaction

        bucket = self.buckets[self._hash(t)]
        for group in bucket:
            if group.should_own(t, perspective, self.window, block):
                return group.add(t, perspective, block)

        group = _DupeGroup()
        bucket.append(group)
        return group.add(t, perspective, block)

    def getPerspectives(self, transactions):
        """ List the perspectives of associated transactions.

        Args:
            transactions: A list references to transactions within
                this structure.

        Returns:
            3 parallel lists; references to transactions that are
            considered to be the originals, the perspectives of
            those original transactions, and the perspectives associated
            with the provided transactions.
        """
        oref = []
        oper = []
        act = []

        for t in transactions:
            bucket = self.buckets[self._hash(t)]

            for group in bucket:
                o, a = group.find_perspectives(t)
                if [o, a] != [None, None]:
                    oref.append(group.orig)
                    oper.append(o)
                    act.append(a)
                    break

        return oref, oper, act

    def _hash(self, transaction):
        """ Use this function to lookup transactions in the buckets.

        DupeTracker omits transaction dates as part of their hashes.
        """
        t = transaction
        return '{}{}{}'.format(t.src.name, t.dest.name, t.amount)
