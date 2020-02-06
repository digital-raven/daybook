import unittest

import dateparser

from daybook.Account import Account
from daybook.Amount import Amount
from daybook.Transaction import Transaction


amount = Amount('jpy', 10, 'jpy', 10)


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
            t.append(Transaction(dateparser.parse('today'), a, a, amount))

        a.addTransactions(t)
        self.assertEqual(0, a.balances['jpy'])

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
        t = Transaction(dateparser.parse('today'), a, a, amount)
        a.addTransaction(t)
        self.assertEqual(0, a.balances['jpy'])
        self.assertEqual(1, len(a.transactions))

    def test_add_transaction_not_me(self):
        """ Accounts should raise ValueError if not in the transaction
        """
        a = Account('a')
        b = Account('b')
        t = Transaction(dateparser.parse('today'), b, b, amount)

        with self.assertRaises(ValueError):
            a.addTransaction(t)

    def test_balance_between_asset_accounts(self):
        """ Asset accounts should transfer money to each other and zero.
        """
        a = Account('a')
        b = Account('b')
        t = []
        for i in range(1, 10):
            t.append(Transaction(dateparser.parse('today'), a, b, amount))

        a.addTransactions(t)
        b.addTransactions(t)

        self.assertEqual(-90, a.balances['jpy'])
        self.assertEqual(90, b.balances['jpy'])

    def test_balance_liability_payoff(self):
        """ Verify asset account's ability to pay off debt
        """
        a = Account('a')
        liab = Account('l', 'liability')
        void = Account('void', 'asset')

        # create debt, add wealth, pay it off
        t1 = Transaction(dateparser.parse('today'), liab, void, amount)
        t2 = Transaction(dateparser.parse('today'), void, a, amount)
        t3 = Transaction(dateparser.parse('today'), a, liab, amount)

        a.addTransactions([t2, t3])
        liab.addTransactions([t1, t3])
        void.addTransactions([t1, t2])

        self.assertEqual(0, void.balances['jpy'])
        self.assertEqual(0, a.balances['jpy'])
        self.assertEqual(0, liab.balances['jpy'])

    def test_balance_rounding(self):
        """ Very small numbers should not fail balance tests.
        """
        a = Account('a')
        b = Account('b')

        x = Amount('jpy', 3.33, 'jpy', 3.33)
        y = Amount('jpy', 4.32, 'jpy', 4.32)
        z = Amount('jpy', 0.99, 'jpy', 0.99)

        t = []
        t.append(Transaction(dateparser.parse('today'), a, b, x))
        t.append(Transaction(dateparser.parse('today'), b, a, y))
        t.append(Transaction(dateparser.parse('today'), a, b, z))

        a.addTransactions(t)
        b.addTransactions(t)

        s = sum([s.balances['jpy'] for s in [a, b]])

        self.assertEqual(0, s)

        # verify this sum would otherwise be non-zero
        self.assertFalse(3.33 - 4.32 + 0.99 == 0)

    def test_self_trade(self):
        """ An account should be able to trade with itself.
        """
        a = Account('a')
        x = Amount('jpy', 3.33, 'usd', 10)

        t = Transaction(dateparser.parse('today'), a, a, x)
        a.addTransaction(t)

        self.assertEqual(-3.33, a.balances['jpy'])
        self.assertEqual(10, a.balances['usd'])


if __name__ == '__main__':
    unittest.main()
