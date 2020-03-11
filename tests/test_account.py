import unittest
from datetime import datetime

from daybook.Account import Account
from daybook.Amount import Amount
from daybook.Transaction import Transaction


amount = Amount('jpy', -10, 'jpy', 10)


class TestAccount(unittest.TestCase):

    def test_balance_zeroes_with_self(self):
        """ An account with transactions only with itself should zero
        """
        a = Account('asset.name')
        t = []
        for i in range(1, 10):
            t.append(Transaction(datetime.today(), a, a, amount))

        a.addTransactions(t)
        self.assertEqual(0, a.balances['jpy'])

    def test_create_from_str_empty(self):
        """ An account created empty string should raise ValueError
        """
        with self.assertRaises(ValueError):
            Account('')

    def test_create_from_str_one(self):
        """ A string with no type should raise.
        """
        with self.assertRaises(ValueError):
            a = Account('name')

    def test_create_from_str_two(self):
        """ A string can specify a type and name.
        """
        a = Account('asset.name')
        self.assertEqual('asset.name', a.name)
        self.assertEqual('asset', a.type)

    def test_create_from_str_spaces(self):
        """ An account name cannot contain spaces.
        """
        with self.assertRaises(ValueError):
            Account('asset.ihave spaces')

    def test_add_transaction(self):
        """ Test adding a single transaction to an account.
        """
        a = Account('asset.a')
        t = Transaction(datetime.today(), a, a, amount)
        a.addTransaction(t)
        self.assertEqual(0, a.balances['jpy'])
        self.assertEqual(1, len(a.transactions))

    def test_add_transaction_not_me(self):
        """ Accounts should raise ValueError if not in the transaction
        """
        a = Account('asset.a')
        b = Account('asset.b')
        t = Transaction(datetime.today(), b, b, amount)

        with self.assertRaises(ValueError):
            a.addTransaction(t)

    def test_balance_between_asset_accounts(self):
        """ Asset accounts should transfer money to each other and zero.
        """
        a = Account('asset.a')
        b = Account('asset.b')
        t = []
        for i in range(1, 10):
            t.append(Transaction(datetime.today(), a, b, amount))

        a.addTransactions(t)
        b.addTransactions(t)

        self.assertEqual(-90, a.balances['jpy'])
        self.assertEqual(90, b.balances['jpy'])

    def test_balance_liability_payoff(self):
        """ Verify asset account's ability to pay off debt
        """
        a = Account('asset.a')
        liab = Account('liability.l')
        void = Account('asset.void')

        # create debt, add wealth, pay it off
        t1 = Transaction(datetime.today(), liab, void, amount)
        t2 = Transaction(datetime.today(), void, a, amount)
        t3 = Transaction(datetime.today(), a, liab, amount)

        a.addTransactions([t2, t3])
        liab.addTransactions([t1, t3])
        void.addTransactions([t1, t2])

        self.assertEqual(0, void.balances['jpy'])
        self.assertEqual(0, a.balances['jpy'])
        self.assertEqual(0, liab.balances['jpy'])

    def test_balance_rounding(self):
        """ Very small numbers should not fail balance tests.
        """
        a = Account('asset.a')
        b = Account('asset.b')

        x = Amount('jpy', 3.33, 'jpy', -3.33)
        y = Amount('jpy', 4.32, 'jpy', -4.32)
        z = Amount('jpy', 0.99, 'jpy', -0.99)

        t = []
        t.append(Transaction(datetime.today(), a, b, x))
        t.append(Transaction(datetime.today(), a, b, y))
        t.append(Transaction(datetime.today(), a, b, z))

        a.addTransactions(t)
        b.addTransactions(t)

        s = sum([s.balances['jpy'] for s in [a, b]])

        self.assertEqual(0, s)

        # verify this sum would otherwise be non-zero
        self.assertFalse(3.33 - 4.32 + 0.99 == 0)

    def test_self_trade(self):
        """ An account should be able to trade with itself.
        """
        a = Account('asset.a')
        x = Amount('jpy', -3.33, 'usd', 10)

        t = Transaction(datetime.today(), a, a, x)
        a.addTransaction(t)

        self.assertEqual(-3.33, a.balances['jpy'])
        self.assertEqual(10, a.balances['usd'])

    def test_type_prefix(self):
        """ Prefixes of types should match.
        """
        a = Account('a.a')
        self.assertEqual('asset', a.type)
        self.assertEqual('asset.a', a.name)

        a = Account('l.a')
        self.assertEqual('liability', a.type)
        self.assertEqual('liability.a', a.name)

        with self.assertRaises(ValueError):
            a = Account('asss.a')

if __name__ == '__main__':
    unittest.main()
