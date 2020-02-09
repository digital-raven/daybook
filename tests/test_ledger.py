import os
import unittest
from datetime import datetime

from daybook.Ledger import Ledger
from daybook.Hints import Hints


pcurr = 'usd'
resources = '{}/resources'.format(os.path.dirname(__file__))


class TestLedger(unittest.TestCase):

    def test_single_transaction(self):
        """ Verify correct behavior for single csv.
        """
        ledger = Ledger(pcurr)
        ledger.loadCsv('{}/single.csv'.format(resources), Hints('{}/hints'.format(resources)))

        src = ledger.accounts['my-employer']
        dest = ledger.accounts['my-checking']
        t = ledger.transactions[0]

        self.assertEqual(2, len(ledger.accounts))

        self.assertEqual('my-employer', src.name)
        self.assertEqual('income', src.type)
        self.assertEqual(-100, src.balances['usd'])

        self.assertEqual('my-checking', dest.name)
        self.assertEqual('asset', dest.type)
        self.assertEqual(100, dest.balances['usd'])

        self.assertTrue('paystub' in t.tags)
        self.assertEqual(t.src, src)
        self.assertEqual(t.dest, dest)
        self.assertEqual(t.date, datetime(2019, 10, 8))

    def test_hints_match(self):
        """ Verify that account names can be inferred from hints.
        """
        ledger = Ledger(pcurr)
        ledger.loadCsv('{}/single-hints/my-checking.csv'.format(resources), Hints('{}/hints'.format(resources)))

        self.assertTrue('void' in ledger.accounts)
        self.assertTrue('my-checking' in ledger.accounts)
        self.assertTrue('grocery' in ledger.accounts)

        src = ledger.accounts['my-checking']
        dest = ledger.accounts['grocery']

        self.assertEqual(-45.77, src.balances['usd'])
        self.assertEqual(45.77, dest.balances['usd'])

        self.assertEqual('asset', src.type)
        self.assertEqual('expense', dest.type)

    def test_bad_csv(self):
        """ A csv with a row that cannot suggest an account should error.

        The ledger should also remain unaffected by that csv entirely.
        """
        ledger = Ledger(pcurr)
        with self.assertRaises(ValueError):
            ledger.loadCsv('{}/badsrc.csv'.format(resources))

        self.assertEqual(0, len(ledger.accounts))
        self.assertEqual(0, len(ledger.transactions))

    def test_this_substitution(self):
        """Verify behavior for transactions on 'this'.

        Transactions that contain 'this' as the account name should
        substitute the basename of the csv.
        """
        ledger = Ledger(pcurr)
        ledger.loadCsv('{}/employer-payroll.csv'.format(resources), Hints('{}/hints'.format(resources)))

        self.assertTrue('employer-payroll' in ledger.accounts)

        emp = ledger.accounts['employer-payroll']
        self.assertEqual('employer-payroll', emp.name)
        self.assertEqual('income', emp.type)
        self.assertEqual(-100, emp.balances['usd'])

    def test_multiple_transactions(self):
        """ Multiple transactions from a single csv should zero.
        """

        ledger = Ledger(pcurr)
        ledger.loadCsv('{}/loan-payoff.csv'.format(resources), Hints('{}/hints'.format(resources)))

        self.assertEqual(4, len(ledger.accounts))
        self.assertEqual(5, len(ledger.transactions))

        for a in ['car-loan', 'void', 'my-company-payroll', 'my-checking']:
            self.assertTrue(a in ledger.accounts)
            ac = ledger.accounts[a]
            self.assertEqual(a, ac.name)

        s = sum([x.balances['usd'] for y, x in ledger.accounts.items()])
        self.assertEqual(0, s)

    def test_multiple_csvs_redundant(self):
        """ Verify duplicated transactions across csvs.

        Transactions read from multiple csvs should not enter twice if
        those transactions have the same dates, src and destination account
        names, and identical amounts.
        """
        path = '{}/multi-csv'.format(resources)
        csvs = [
            '{}/car-loan.csv'.format(path),
            '{}/my-checking.csv'.format(path),
            '{}/my-company-payroll.csv'.format(path),
        ]

        ledger = Ledger(pcurr)
        ledger.loadCsvs(csvs)

        self.assertEqual(4, len(ledger.accounts))
        self.assertEqual(4, len(ledger.transactions))

        self.assertEqual(0, ledger.accounts['car-loan'].balances['usd'])
        self.assertEqual(
            100, ledger.accounts['my-checking'].balances['usd'])
        self.assertEqual(
            -200, ledger.accounts['my-company-payroll'].balances['usd'])

    def test_multiple_csvs_tags(self):
        """ Tags from duplicate transactions should sum.
        """
        path = '{}/multi-csv-tags'.format(resources)
        csvs = [
            '{}/checking.csv'.format(path),
            '{}/employer-payroll.csv'.format(path),
        ]

        ledger = Ledger(pcurr)
        ledger.loadCsvs(csvs)

        expected = ['payment', 'tags', 'i', 'got', 'paid']

        self.assertEqual(len(expected), len(ledger.transactions[0].tags))
        for e in expected:
            self.assertTrue(e in ledger.transactions[0].tags)

    def test_transaction_from_dump(self):
        """ Verify a ledger's dump can populate another ledger.
        """
        path = '{}/multi-csv'.format(resources)
        csvs = [
            '{}/car-loan.csv'.format(path),
            '{}/my-checking.csv'.format(path),
            '{}/my-company-payroll.csv'.format(path),
        ]

        ledger1 = Ledger(pcurr)
        ledger1.loadCsvs(csvs)

        ledger2 = Ledger(pcurr)
        ledger2.load(ledger1.dump())

        self.assertEqual(ledger1.dump(), ledger2.dump())

    def test_target_direction_no_dest(self):
        """ target implies dest if src is present.
        """
        lines = (
            'date,src,target,amount\n'
            'today,checking,food,10')
        ledger = Ledger(pcurr)
        ledger.load(lines)
        self.assertEqual(10, ledger.accounts['food'].balances['usd'])
        self.assertEqual(-10, ledger.accounts['checking'].balances['usd'])

    def test_target_direction_no_src(self):
        """ target implies src if dest is present.
        """
        lines = (
            'date,dest,target,amount\n'
            'today,dest,src,10')
        ledger = Ledger(pcurr)
        ledger.load(lines)
        self.assertEqual(-10, ledger.accounts['src'].balances['usd'])
        self.assertEqual(10, ledger.accounts['dest'].balances['usd'])

    def test_target_only(self):
        """ Sign determines direction if no src or dest.
        """
        lines = (
            'date,target,amount\n'
            'today,food,-10\n'
            'today,saving,10')
        ledger = Ledger(pcurr)
        ledger.load(lines, thisname='checking')
        self.assertEqual(0, ledger.accounts['checking'].balances['usd'])
        self.assertEqual(10, ledger.accounts['food'].balances['usd'])
        self.assertEqual(-10, ledger.accounts['saving'].balances['usd'])

    def test_no_src_dest_target(self):
        """ 'this' should be used if no accounts specified.
        """
        lines = (
            'date,amount\n'
            'today,10 usd 40 shares')
        ledger = Ledger(pcurr)
        ledger.load(lines, thisname='brokerage')
        self.assertEqual(-10, ledger.accounts['brokerage'].balances['usd'])
        self.assertEqual(40, ledger.accounts['brokerage'].balances['shares'])

    def test_empty_src_void(self):
        """ If the src entry is empty, then void should be used.
        """
        lines = (
            'date,src,amount\n'
            'today,,10')
        ledger = Ledger(pcurr)
        ledger.load(lines, thisname='checking')
        self.assertEqual(10, ledger.accounts['checking'].balances['usd'])
        self.assertEqual(-10, ledger.accounts['void'].balances['usd'])

    def test_empty_dest_void(self):
        """ Same as above, but with dest.
        """
        lines = (
            'date,dest,amount\n'
            'today,,10')
        ledger = Ledger(pcurr)
        ledger.load(lines, thisname='checking')
        self.assertEqual(-10, ledger.accounts['checking'].balances['usd'])
        self.assertEqual(10, ledger.accounts['void'].balances['usd'])


if __name__ == '__main__':
    unittest.main()
