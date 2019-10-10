import unittest

from daybook.Ledger import Account, Transaction


class TestAccount(unittest.TestCase):

    def test_add_redundant_tag_creation(self):
        """ Account tags should be unique on creation.
        """
        a = Account('name', 'asset', ['tag1', 'tag1', 'tag2'])
        utags = [x for x in a.tags if x == 'tag1']
        self.assertEqual(1, len(utags))

    def test_add_redundant_tags(self):
        """ addTags should produce a list of unique tags.
        """
        a = Account('name', 'asset', ['tag1', 'tag1', 'tag2'])
        a.addTags('tag1')
        a.addTags(['tag1', 'tag1'])
        utags = [x for x in a.tags if x == 'tag1']
        self.assertEqual(1, len(utags))

    def test_balance_zeroes_with_self(self):
        """ An account with transactions only with itself should zero
        """
        a = Account('name')
        t = []
        for i in range(1, 10):
            t.append(Transaction('today', a, a, i))

        a.addTransactions(t)

        for type in Account.types:
            a.type = type
            self.assertEqual(0, a.balance())

    def test_create_from_list_zero(self):
        """ An account created from list 0 should raise ValueError
        """
        with self.assertRaises(ValueError):
            Account.createFromList([])

    def test_create_from_list_one(self):
        """ An account created from list with len 1 should only have a name.
        """
        a = Account.createFromList(['name'])
        self.assertEqual('name', a.name)
        self.assertEqual('asset', a.type)
        self.assertTrue(not a.tags)

    def test_create_from_list_two(self):
        """ An account created from list with len 2 can have type or tags.
        """
        a = Account.createFromList(['name:asdf', 'tag1:tag2'])
        self.assertEqual('name:asdf', a.name)
        self.assertEqual('asset', a.type)
        self.assertEqual({'tag1', 'tag2'}, a.tags)

        a = Account.createFromList(['name', 'liability'])
        self.assertEqual('name', a.name)
        self.assertEqual('liability', a.type)
        self.assertTrue(not a.tags)

    def test_create_from_list_three(self):
        """ An account created from list 3 should have name, type, and tags.
        """
        a = Account.createFromList(['name', 'liability', 'tag1:tag2'])
        self.assertEqual('name', a.name)
        self.assertEqual('liability', a.type)
        self.assertEqual({'tag1', 'tag2'}, a.tags)

    def test_create_from_list_four(self):
        """ An account created from list 4 should raise ValueError
        """
        with self.assertRaises(ValueError):
            Account.createFromList(['name', 'expense', 't1:t2', 'extra'])

    def test_add_transaction(self):
        """ Test adding a single transaction to an account.
        """
        a = Account('a')
        t = Transaction('today', a, a, 10)
        a.addTransaction(t)
        self.assertEqual(0, a.balance())
        self.assertEqual(1, len(a.transactions))

    def test_add_transaction_not_me(self):
        """ Accounts should raise ValueError if not in the transaction
        """
        a = Account('a')
        b = Account('b')
        t = Transaction('today', b, b, 10)

        with self.assertRaises(ValueError):
            a.addTransaction(t)

    def test_add_transactions(self):
        """ Positive test case for addTransactions.

        Accounts should only add the transactions which they are in.
        """
        a = Account('a')
        b = Account('b')

        t = []
        for i in range(1, 10):
            t.append(Transaction('today', a, a, i))
        for i in range(1, 10):
            t.append(Transaction('today', b, b, i))

        a.addTransactions(t)
        b.addTransactions(t)

        ta = a.transactions
        tb = b.transactions

        self.assertEqual(9, len(a.transactions))
        self.assertEqual(9, len(b.transactions))
        self.assertTrue(not [x for x in ta if b in [x.src, x.dest]])
        self.assertTrue(not [x for x in tb if a in [x.src, x.dest]])

    def test_balance_between_asset_accounts(self):
        """ Asset accounts should transfer money to each other and zero.
        """
        a = Account('a')
        b = Account('b')
        t = []
        x = 0
        for i in range(1, 10):
            t.append(Transaction('today', a, b, i))
            x = x + i

        a.addTransactions(t)
        b.addTransactions(t)

        self.assertEqual(-x, a.balance())
        self.assertEqual(x, b.balance())

    def test_balance_liability_payoff(self):
        """ Verify asset account's ability to pay off debt
        """
        a = Account('a')
        liab = Account('l', 'liability')
        void = Account('void', 'asset')

        # create debt, add wealth, pay it off
        t1 = Transaction('today', liab, void, 100)
        t2 = Transaction('today', void, a, 100)
        t3 = Transaction('today', a, liab, 100)

        a.addTransactions([t1, t2, t3])
        liab.addTransactions([t1, t2, t3])
        void.addTransactions([t1, t2, t3])

        self.assertEqual(0, void.balance())
        self.assertEqual(0, a.balance())
        self.assertEqual(0, liab.balance())

    def test_balance_rounding(self):
        """ Very small numbers should not fail balance tests.
        """
        a = Account('a')
        b = Account('b')

        t = []
        t.append(Transaction('today', a, b, 3.33))
        t.append(Transaction('today', b, a, 4.32))
        t.append(Transaction('today', a, b, 0.99))

        a.addTransactions(t)
        b.addTransactions(t)

        x = sum([x.balance() for x in [a, b]])

        self.assertEqual(0, x)

        # verify this sum would otherwise be non-zero
        self.assertFalse(3.33 - 4.32 + 0.99 == 0)


if __name__ == '__main__':
    unittest.main()
