import os
import unittest
from datetime import datetime

from daybook.Ledger import Ledger
from daybook.Hints import Hints


pcurr = 'usd'
resources = '{}/resources'.format(os.path.dirname(__file__))


class TestLedger(unittest.TestCase):

    def test_date_only(self):
        """ Date should be the only required field for a transaction.

        The transaction should be created like this...

            date,src,dest,amount,tags,notes
            date,void.void,void.void,0:pcurr 0:pcurr,,,
        """
        ledger = Ledger(pcurr)
        lines = (
            'date\n'
            '03-17-2016 21:02\n')
        ledger.load(lines)
        self.assertEqual(1, len(ledger.accounts))
        self.assertEqual(1, len(ledger.transactions))

        t = ledger.transactions[0]

        self.assertEqual(datetime(2016, 3, 17, 21, 2, 0), t.date)
        self.assertEqual('void', t.src.name)
        self.assertEqual('void', t.src.type)
        self.assertEqual(t.src, t.dest)
        self.assertEqual(0, t.src.balances[pcurr])
        self.assertEqual(0, t.dest.balances[pcurr])
        self.assertEqual(0, t.amount.src_amount)
        self.assertEqual(0, t.amount.dest_amount)
        self.assertEqual(pcurr, t.amount.src_currency)
        self.assertEqual(pcurr, t.amount.dest_currency)
        self.assertEqual(set(), t.tags)
        self.assertEqual('', t.notes)

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

        self.assertEqual('liability', ledger.accounts['car-loan'].type)
        self.assertEqual('asset', ledger.accounts['my-checking'].type)
        self.assertEqual('income', ledger.accounts['my-company-payroll'].type)

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

    def test_src_only(self):
        """ If only src is provided, then dest should be thisname.
        """
        lines = (
            'date,src,amount\n'
            'today,checking,10')
        ledger = Ledger(pcurr)
        ledger.load(lines, thisname='income.employer')
        self.assertEqual(10, ledger.accounts['checking'].balances['usd'])
        self.assertEqual(-10, ledger.accounts['employer'].balances['usd'])

    def test_dest_only(self):
        """ If only dest is provided, then src should be thisname.
        """
        lines = (
            'date,dest,amount\n'
            'today,expense.grocery,-10')
        ledger = Ledger(pcurr)
        ledger.load(lines, thisname='checking')
        self.assertEqual('void', ledger.accounts['checking'].type)
        self.assertEqual('expense', ledger.accounts['grocery'].type)
        self.assertEqual(-10, ledger.accounts['checking'].balances['usd'])
        self.assertEqual(10, ledger.accounts['grocery'].balances['usd'])

    def test_dest_only_4_amount_fields(self):
        """ Dest and src should be able to handle different currencies.
        """
        lines = (
            'date,dest,amount\n'
            'today,expense.grocery,-10 usd 20 mxn')
        ledger = Ledger(pcurr)
        ledger.load(lines, thisname='asset.checking')
        self.assertEqual(-10, ledger.accounts['checking'].balances['usd'])
        self.assertEqual(20, ledger.accounts['grocery'].balances['mxn'])

    def test_no_src_and_no_dest(self):
        """ If neither src or dest are provided, then each should use thisname.
        """
        lines = (
            'date,amount\n'
            'today,-10 usd 20 tsla')
        ledger = Ledger(pcurr)
        ledger.load(lines, thisname='asset.brokerage')
        self.assertEqual(-10, ledger.accounts['brokerage'].balances['usd'])
        self.assertEqual(20, ledger.accounts['brokerage'].balances['tsla'])

    def test_empty_src_void(self):
        """ Load should raise if the src entry is empty.
        """
        lines = (
            'date,src,amount\n'
            'today,,10')
        ledger = Ledger(pcurr)
        with self.assertRaises(ValueError):
            ledger.load(lines, thisname='asset.checking')

    def test_empty_dest_void(self):
        """ Same as above, but with dest.
        """
        lines = (
            'date,dest,amount\n'
            'today,,10')
        ledger = Ledger(pcurr)
        with self.assertRaises(ValueError):
            ledger.load(lines, thisname='checking')

    def test_no_amount_field(self):
        """ The absence of an 'amount' field should default to 0 for all.

        Useful for creating a bunch of empty accounts. This will also create
        an account called 'accounts'.
        """
        ledger = Ledger(pcurr)
        lines = (
            'date,dest\n'
            'today,checking\n'
            'today,liability.car-loan\n')

        # This kind of data would likely come from accounts.csv.
        ledger.load(lines, thisname='accounts')

        self.assertEqual('void', ledger.accounts['checking'].type)
        self.assertEqual('liability', ledger.accounts['car-loan'].type)

        self.assertEqual(2, len(ledger.transactions))
        self.assertEqual(3, len(ledger.accounts))
        for t in ledger.transactions:
            self.assertEqual('accounts', t.src.name)
            self.assertEqual(0, t.src.balances['usd'])
            self.assertEqual(0, t.dest.balances['usd'])

    def test_thisname_type_assignment(self):
        """ thisname should be capable of containing a type.
        """
        ledger = Ledger(pcurr)
        lines = (
            'date,dest\n'
            'today,this\n')
        ledger.load(lines, thisname='income.employer')
        self.assertEqual(1, len(ledger.accounts))
        self.assertEqual('income', ledger.accounts['employer'].type)

    def test_thisname_notype(self):
        """ thisname should replace instances of 'this' between dots.

        The following logic creates a transaction from

            void.checking => asset.checking.checking
        """
        ledger = Ledger(pcurr)
        lines = (
            'date,dest\n'
            'today,asset.this.this\n')
        ledger.load(lines, thisname='checking')
        self.assertEqual(2, len(ledger.accounts))
        self.assertEqual('void', ledger.accounts['checking'].type)
        self.assertEqual('asset', ledger.accounts['checking.checking'].type)

    def test_thisname_no_dots(self):
        """ thisname should just blindly replace instances of 'this'

        The following logic creates a transaction from

            void.checking => asset.ethis
        """
        ledger = Ledger(pcurr)
        lines = (
            'date,dest\n'
            'today,asset.ethis\n')
        ledger.load(lines, thisname='checking')
        self.assertEqual(2, len(ledger.accounts))
        self.assertEqual('void', ledger.accounts['checking'].type)
        self.assertEqual('asset', ledger.accounts['ethis'].type)

    def test_overwrite_void(self):
        """ "Concrete" types should overwrite void on ledger entry.
        """
        ledger = Ledger(pcurr)
        lines1 = (
            'date,dest,amount\n'
            'today,employer,10\n')

        lines2 = (
            'date,dest,amount\n'
            'today,income.employer,20\n')
        ledger.load(lines1, thisname='asset.checking')
        self.assertEqual('void', ledger.accounts['employer'].type)

        ledger.load(lines2, thisname='asset.checking')
        self.assertEqual('income', ledger.accounts['employer'].type)
        self.assertEqual(-30, ledger.accounts['employer'].balances[pcurr])
        self.assertEqual(30, ledger.accounts['checking'].balances[pcurr])

    def test_void_cant_overwrite(self):
        """ "Void" shouldn't be capable of overwriting an existing type.
        """
        ledger = Ledger(pcurr)
        lines1 = (
            'date,dest\n'
            'today,asset.checking\n')

        lines2 = (
            'date,dest\n'
            'today,void.checking\n')
        ledger.load(lines1)
        self.assertEqual('asset', ledger.accounts['checking'].type)

        ledger.load(lines2)
        self.assertEqual('asset', ledger.accounts['checking'].type)

    def test_ignore_new_types(self):
        """ Types served on first-come-first-served basis.
        """
        ledger = Ledger(pcurr)
        lines1 = (
            'date,dest\n'
            'today,asset.checking\n')

        lines2 = (
            'date,dest\n'
            'today,income.checking\n')
        ledger.load(lines1)
        self.assertEqual('asset', ledger.accounts['checking'].type)

        ledger.load(lines2)
        self.assertEqual('asset', ledger.accounts['checking'].type)

    def test_strip_account_names(self):
        """ Extraneous spaces should not raise.
        """
        ledger = Ledger(pcurr)
        lines = (
            'date,dest\n'
            'today,    asset.checking    \n')
        ledger.load(lines)
        self.assertEqual('asset', ledger.accounts['checking'].type)

    def test_spaces_raise(self):
        """ Spaces in an account name should raise.
        """
        ledger = Ledger(pcurr)
        lines = (
            'date,dest\n'
            'today,asset. checking\n')
        with self.assertRaises(ValueError):
            ledger.load(lines)

    def test_type_only_raise(self):
        """ It should raise if only a type were provided.
        """
        ledger = Ledger(pcurr)
        lines = (
            'date,dest\n'
            'today,asset\n')
        with self.assertRaises(ValueError):
            ledger.load(lines)

    def test_void_only_is_allowed(self):
        """ But an exception is made for 'void'.
        """
        ledger = Ledger(pcurr)
        lines = (
            'date,dest\n'
            'today,void\n')
        ledger.load(lines, thisname='asset.checking')
        self.assertEqual('void', ledger.accounts['void'].type)


if __name__ == '__main__':
    unittest.main()
