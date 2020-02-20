import unittest

import dateparser

from daybook.Account import Account
from daybook.Amount import Amount
from daybook.Transaction import Transaction


amount = Amount('jpy', -10, 'jpy', 10)


class TestAccount(unittest.TestCase):

    def test_balance_zeroes_with_self(self):
        """ An account with transactions only with itself should zero
        """
        a = Account('name', 'asset')
        t = []
        for i in range(1, 10):
            t.append(Transaction(dateparser.parse('today'), a, a, amount))

        a.addTransactions(t)
        self.assertEqual(0, a.balances['jpy'])

    def test_create_from_str_empty(self):
        """ An account created empty string should raise ValueError
        """
        with self.assertRaises(ValueError):
            Account.createFromStr('')

    def test_create_from_str_one(self):
        """ A string with no type should default to type void.
        """
        a = Account.createFromStr('name')
        self.assertEqual('name', a.name)
        self.assertEqual('void', a.type)

    def test_create_from_str_two(self):
        """ A string can specify a type and name.
        """
        a = Account.createFromStr('asset.name')
        self.assertEqual('name', a.name)
        self.assertEqual('asset', a.type)

    def test_create_from_str_spaces(self):
        """ An account name cannot contain spaces.
        """
        with self.assertRaises(ValueError):
            Account.createFromStr('asset.ihave spaces')

    def test_add_transaction(self):
        """ Test adding a single transaction to an account.
        """
        a = Account('a', 'asset')
        t = Transaction(dateparser.parse('today'), a, a, amount)
        a.addTransaction(t)
        self.assertEqual(0, a.balances['jpy'])
        self.assertEqual(1, len(a.transactions))

    def test_add_transaction_not_me(self):
        """ Accounts should raise ValueError if not in the transaction
        """
        a = Account('a', 'asset')
        b = Account('b', 'asset')
        t = Transaction(dateparser.parse('today'), b, b, amount)

        with self.assertRaises(ValueError):
            a.addTransaction(t)

    def test_balance_between_asset_accounts(self):
        """ Asset accounts should transfer money to each other and zero.
        """
        a = Account('a', 'asset')
        b = Account('b', 'asset')
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
        a = Account('a', 'asset')
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
        a = Account('a', 'asset')
        b = Account('b', 'asset')

        x = Amount('jpy', 3.33, 'jpy', -3.33)
        y = Amount('jpy', 4.32, 'jpy', -4.32)
        z = Amount('jpy', 0.99, 'jpy', -0.99)

        t = []
        t.append(Transaction(dateparser.parse('today'), a, b, x))
        t.append(Transaction(dateparser.parse('today'), a, b, y))
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
        a = Account('a', 'asset')
        x = Amount('jpy', -3.33, 'usd', 10)

        t = Transaction(dateparser.parse('today'), a, a, x)
        a.addTransaction(t)

        self.assertEqual(-3.33, a.balances['jpy'])
        self.assertEqual(10, a.balances['usd'])


if __name__ == '__main__':
    unittest.main()
