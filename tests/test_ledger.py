import os
import unittest
from datetime import datetime

from daybook.Amount import Amount
from daybook.Ledger import Ledger, suggest_notes
from daybook.Hints import Hints
from daybook.Transaction import Transaction


pcurr = 'usd'
resources = '{}/resources'.format(os.path.dirname(__file__))


class TestSuggestNotes(unittest.TestCase):
    """ For testing suggest_notes function.
    """
    def test_src_and_dest(self):
        """ It should use both src and dest.
        """
        notes = suggest_notes('src', 'dest', None)
        self.assertEqual('src -> dest', notes)

    def test_trim(self):
        """ It should trim white space.
        """
        notes = suggest_notes('   src   ', '  dest ', None)
        self.assertEqual('src -> dest', notes)

    def test_only_src(self):
        """ It should be capable of only using src.
        """
        notes = suggest_notes('src', '', None)
        self.assertEqual('src', notes)

    def test_only_dest(self):
        """ It should be capable of only using dest.
        """
        notes = suggest_notes('', 'dest', None)
        self.assertEqual('dest', notes)

    def test_only_dest(self):
        """ It should be capable of only using dest.
        """
        notes = suggest_notes('', 'dest', None)
        self.assertEqual('dest', notes)

    def test_currs_when_neither(self):
        """ It should use currencies if not(src or dest).
        """
        a = Amount('usd', -1, 'mxn', 1)
        notes = suggest_notes('', '', a)
        self.assertEqual('usd -> mxn', notes)

    def test_currs_when_equal(self):
        """ It should use currencies if src == dest.
        """
        a = Amount('usd', -1, 'tsla', 1)
        notes = suggest_notes('asset.investment', 'asset.investment', a)
        self.assertEqual('usd -> tsla', notes)

    def test_empty_return(self):
        """ It should return empty string if nothing proivded.
        """
        notes = suggest_notes(None, None, None)
        self.assertEqual('', notes)


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
        self.assertEqual('void.void', t.src.name)
        self.assertEqual('void', t.src.type)
        self.assertEqual(t.src, t.dest)
        self.assertEqual(0, t.src.balances[pcurr])
        self.assertEqual(0, t.dest.balances[pcurr])
        self.assertEqual(0, t.amount.src_amount)
        self.assertEqual(0, t.amount.dest_amount)
        self.assertEqual(pcurr, t.amount.src_currency)
        self.assertEqual(pcurr, t.amount.dest_currency)
        self.assertEqual(set(), t.tags)
        self.assertEqual('usd -> usd', t.notes)

    def test_single_transaction(self):
        """ Verify correct behavior for a single transaction.
        """
        ledger = Ledger(pcurr)
        lines = (
            'date,src,dest,amount,tags\n'
            '11/11/11,asset.checking,expense.food,-10,mcdonalds:fast-food')
        ledger.load(lines)

        self.assertEqual(1, len(ledger.transactions))

        checking = ledger.accounts['asset.checking']
        food = ledger.accounts['expense.food']

        exp = Transaction(
            datetime(2011, 11, 11, 0, 0, 0),
            checking, food,
            Amount('usd', -10, 'usd', 10))

        self.assertEqual(exp, ledger.transactions[0])

        self.assertEqual(1, len(checking.balances))
        self.assertEqual(1, len(food.balances))
        self.assertEqual(-10, checking.balances[pcurr])
        self.assertEqual(10, food.balances[pcurr])

    def test_single_transaction_csv(self):
        """ Verify correct behavior for single transaction in a csv.
        """
        ledger = Ledger(pcurr)
        ledger.loadCsv('{}/single.csv'.format(resources), Hints('{}/hints'.format(resources)))

        src = ledger.accounts['income.my-employer']
        dest = ledger.accounts['asset.my-checking']
        t = ledger.transactions[0]

        self.assertEqual(2, len(ledger.accounts))

        self.assertEqual('income.my-employer', src.name)
        self.assertEqual('income', src.type)
        self.assertEqual(-100, src.balances['usd'])

        self.assertEqual('asset.my-checking', dest.name)
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

        self.assertTrue('void.void' in ledger.accounts)
        self.assertTrue('asset.my-checking' in ledger.accounts)
        self.assertTrue('expense.grocery' in ledger.accounts)

        src = ledger.accounts['asset.my-checking']
        dest = ledger.accounts['expense.grocery']

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

        self.assertTrue('income.employer-payroll' in ledger.accounts)

        emp = ledger.accounts['income.employer-payroll']
        self.assertEqual('income.employer-payroll', emp.name)
        self.assertEqual('income', emp.type)
        self.assertEqual(-100, emp.balances['usd'])

    def test_multiple_transactions(self):
        """ Multiple transactions from a single csv should zero.
        """

        ledger = Ledger(pcurr)
        ledger.loadCsv('{}/loan-payoff.csv'.format(resources), Hints('{}/hints'.format(resources)))

        self.assertEqual(4, len(ledger.accounts))
        self.assertEqual(5, len(ledger.transactions))

        for a in ['liability.car-loan', 'void.void', 'income.my-company-payroll', 'asset.my-checking']:
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

        self.assertEqual('liability', ledger.accounts['liability.car-loan'].type)
        self.assertEqual('asset', ledger.accounts['asset.my-checking'].type)
        self.assertEqual('income', ledger.accounts['income.my-company-payroll'].type)

        self.assertEqual(0, ledger.accounts['liability.car-loan'].balances['usd'])
        self.assertEqual(
            100, ledger.accounts['asset.my-checking'].balances['usd'])
        self.assertEqual(
            -200, ledger.accounts['income.my-company-payroll'].balances['usd'])

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

        # May fail because tag order is non-deterministic.
        self.assertEqual(ledger1.dump(), ledger2.dump())

    def test_src_only(self):
        """ If only src is provided, then dest should be thisname.
        """
        lines = (
            'date,src,amount\n'
            '11/11/11,asset.checking,10')
        ledger = Ledger(pcurr)
        ledger.load(lines, thisname='income.employer')
        self.assertEqual(10, ledger.accounts['asset.checking'].balances['usd'])
        self.assertEqual(-10, ledger.accounts['income.employer'].balances['usd'])

    def test_dest_only(self):
        """ If only dest is provided, then src should be thisname.
        """
        lines = (
            'date,dest,amount\n'
            '11/11/11,expense.grocery,-10')
        ledger = Ledger(pcurr)
        ledger.load(lines, thisname='void.checking')
        self.assertEqual('void', ledger.accounts['void.checking'].type)
        self.assertEqual('expense', ledger.accounts['expense.grocery'].type)
        self.assertEqual(-10, ledger.accounts['void.checking'].balances['usd'])
        self.assertEqual(10, ledger.accounts['expense.grocery'].balances['usd'])

    def test_dest_only_4_amount_fields(self):
        """ Dest and src should be able to handle different currencies.
        """
        lines = (
            'date,dest,amount\n'
            '11/11/11,expense.grocery,-10 usd 20 mxn')
        ledger = Ledger(pcurr)
        ledger.load(lines, thisname='asset.checking')
        self.assertEqual(-10, ledger.accounts['asset.checking'].balances['usd'])
        self.assertEqual(20, ledger.accounts['expense.grocery'].balances['mxn'])

    def test_no_src_and_no_dest(self):
        """ If neither src or dest are provided, then each should use thisname.
        """
        lines = (
            'date,amount\n'
            '11/11/11,-10 usd 20 tsla')
        ledger = Ledger(pcurr)
        ledger.load(lines, thisname='asset.brokerage')
        self.assertEqual(-10, ledger.accounts['asset.brokerage'].balances['usd'])
        self.assertEqual(20, ledger.accounts['asset.brokerage'].balances['tsla'])

    def test_empty_src_void(self):
        """ Load should raise if the src entry is empty.
        """
        lines = (
            'date,src,amount\n'
            '11/11/11,,10')
        ledger = Ledger(pcurr)
        with self.assertRaises(ValueError):
            ledger.load(lines, thisname='asset.checking')

    def test_empty_dest_void(self):
        """ Same as above, but with dest.
        """
        lines = (
            'date,dest,amount\n'
            '11/11/11,,10')
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
            '11/11/11,asset.checking\n'
            '11/11/11,liability.car-loan\n')

        # This kind of data would likely come from accounts.csv.
        ledger.load(lines, thisname='void.accounts')

        self.assertEqual('asset', ledger.accounts['asset.checking'].type)
        self.assertEqual('liability', ledger.accounts['liability.car-loan'].type)

        self.assertEqual(2, len(ledger.transactions))
        self.assertEqual(3, len(ledger.accounts))
        for t in ledger.transactions:
            self.assertEqual('void.accounts', t.src.name)
            self.assertEqual(0, t.src.balances['usd'])
            self.assertEqual(0, t.dest.balances['usd'])

    def test_thisname_assignment(self):
        """ Specifying 'this' should use thisname.
        """
        ledger = Ledger(pcurr)
        lines = (
            'date,dest\n'
            '11/11/11,this\n')
        ledger.load(lines, thisname='income.employer')
        self.assertEqual(1, len(ledger.accounts))
        self.assertEqual('income', ledger.accounts['income.employer'].type)

    def test_thisname_no_dots(self):
        """ thisname should not just blindly replace instances of 'this'

        The following logic creates a transaction from

            void.checking => asset.ethis
        """
        ledger = Ledger(pcurr)
        lines = (
            'date,src,dest\n'
            '11/11/11,void.checking,asset.ethis\n')
        ledger.load(lines, thisname='asset.checking')
        self.assertEqual(2, len(ledger.accounts))
        self.assertEqual('void', ledger.accounts['void.checking'].type)
        self.assertEqual('asset', ledger.accounts['asset.ethis'].type)

    def test_competing_types(self):
        """ Types should be a part of account's names.
        """
        ledger = Ledger(pcurr)
        lines1 = (
            'date,dest\n'
            '11/11/11,asset.checking\n')

        lines2 = (
            'date,dest\n'
            '11/11/11,income.checking\n')
        ledger.load(lines1)
        self.assertEqual('asset', ledger.accounts['asset.checking'].type)

        ledger.load(lines2)
        self.assertEqual('income', ledger.accounts['income.checking'].type)
        self.assertTrue('income.checking' in ledger.accounts)
        self.assertTrue('asset.checking' in ledger.accounts)
        self.assertTrue('void.void' in ledger.accounts)
        self.assertEqual(3, len(ledger.accounts))

    def test_strip_account_names(self):
        """ Extraneous spaces should not raise.
        """
        ledger = Ledger(pcurr)
        lines = (
            'date,dest\n'
            '11/11/11,    asset.checking    \n')
        ledger.load(lines)
        self.assertEqual('asset', ledger.accounts['asset.checking'].type)

    def test_spaces_raise(self):
        """ Spaces in an account name should raise.
        """
        ledger = Ledger(pcurr)
        lines = (
            'date,dest\n'
            '11/11/11,asset. checking\n')
        with self.assertRaises(ValueError):
            ledger.load(lines)

    def test_type_only_raise(self):
        """ It should raise if only a type were provided.
        """
        ledger = Ledger(pcurr)
        lines = (
            'date,dest\n'
            '11/11/11,asset\n')
        with self.assertRaises(ValueError):
            ledger.load(lines)

    def test_void_only_is_allowed(self):
        """ But an exception is made for 'void'.
        """
        ledger = Ledger(pcurr)
        lines = (
            'date,dest\n'
            '11/11/11,void\n')
        ledger.load(lines, thisname='asset.checking')
        self.assertEqual('void', ledger.accounts['void.void'].type)

    def test_correction(self):
        """ Src and dest should automatically orient.
        """
        l1 = Ledger(pcurr)
        l2 = Ledger(pcurr)

        # src field == asset.checking
        lines = (
            'date,dest,amount\n'
            '11/11/11,income.employer,1000\n')
        l1.load(lines, thisname='asset.checking')

        # src field == income.employer
        lines = (
            'date,dest,amount\n'
            '11/11/11,asset.checking,-1000\n')
        l2.load(lines, thisname='income.employer')

        t1 = l1.transactions[0]
        t2 = l2.transactions[0]

        self.assertEqual(t1, t2)

        # This check should pass as well; dest field == income.employer
        l3 = Ledger(pcurr)
        lines = (
            'date,src,amount\n'
            '11/11/11,asset.checking,1000\n')
        l3.load(lines, thisname='income.employer')

        t3 = l3.transactions[0]

        self.assertEqual(t1, t3)
        self.assertEqual(t2, t3)

    def test_note_generation_both(self):
        """ Notes should automatically be generated if not provided.
        """
        ledger = Ledger(pcurr)
        lines = (
            'date,src,dest,amount\n'
            '11/11/11,asset.checking,BP BEYOND PETROLEUM ASDF,-10\n')

        ledger.load(lines, hints=Hints('{}/hints'.format(resources)))
        t = ledger.transactions[0]

        # The first 3 words of the original src / dest field should be used.
        self.assertEqual('expense.gasoline', t.dest.name)
        self.assertEqual('asset.checking -> BP BEYOND PETROLEUM', t.notes)

    def test_note_generation_src_only(self):
        """ Note generation should use the orginal src field.
        """
        ledger = Ledger(pcurr)
        lines = (
            'date,src,amount\n'
            '11/11/11,asset.checking,-10\n')

        ledger.load(lines, thisname='expense.gasoline', hints=Hints('{}/hints'.format(resources)))
        t = ledger.transactions[0]

        # The first 3 words of the original field should be used.
        self.assertEqual('asset.checking', t.notes)

    def test_note_generation_dest_only(self):
        """ Note generation should use the orginal dest field.
        """
        ledger = Ledger(pcurr)
        lines = (
            'date,dest,amount\n'
            '11/11/11,BP BEYOND PETROLEUM ASDF,-10\n')

        ledger.load(lines, thisname='asset.checking', hints=Hints('{}/hints'.format(resources)))
        t = ledger.transactions[0]

        # The first 3 words of the original field should be used.
        self.assertEqual('BP BEYOND PETROLEUM', t.notes)

    def test_note_generation_currencies(self):
        """ Notes should use currencies if no src or dest field present.
        """
        ledger = Ledger(pcurr)
        lines = (
            'date,amount\n'
            '11/11/11,-10:usd 50:tsla\n')

        ledger.load(lines, thisname='asset.investment')
        t = ledger.transactions[0]

        self.assertEqual('usd -> tsla', t.notes)

    def test_note_generation_inverted(self):
        """ Note generation should also correct for src -> dest orientation.
        """
        ledger = Ledger(pcurr)
        lines = (
            'date,dest,src,amount\n'
            '11/11/11,asset.checking,BP BEYOND PETROLEUM ASDF,10\n')

        ledger.load(lines, hints=Hints('{}/hints'.format(resources)))
        t = ledger.transactions[0]

        # The orientation should be flipped here.
        self.assertEqual('expense.gasoline', t.dest.name)
        self.assertEqual('asset.checking -> BP BEYOND PETROLEUM', t.notes)

    def test_idempotency1(self):
        """ Re-importing transactions should not affect a ledger.
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

        ledger1.load(ledger2.dump())

        # May fail because tag order is non-deterministic.
        self.assertEqual(ledger1.dump(), ledger2.dump())

    def test_idempotency2(self):
        """ Same as above, but original transactions were empty perspective.
        """
        exp = Ledger(pcurr)
        ledger1 = Ledger(pcurr)
        ledger2 = Ledger(pcurr)

        lines = (
            'date,src,dest,amount\n'
            '14/02/15,asset.investment,asset.checking,-10\n'
            '14/02/15,asset.checking,expense.food,-10\n'
            '14/02/15,asset.checking,expense.food,-10\n')

        exp.load(lines)
        ledger1.load(lines)

        ledger2.load(ledger1.dump())
        ledger1.load(ledger2.dump())

        self.assertEqual(3, len(ledger1.transactions))
        self.assertEqual(ledger1.dump(), ledger2.dump())

        for t in exp.transactions:
            self.assertIn(t, ledger1.transactions)
            self.assertIn(t, ledger2.transactions)

    def test_idempotency3(self):
        """ Same as test_idemptoency1, but each ledger starts with
            some transactions.

            Also indirectly verifies that empty perspective transactions
            can only duplicate on exact dates.
        """
        ledger1 = Ledger(pcurr, duplicate_window=4)
        ledger2 = Ledger(pcurr, duplicate_window=4)

        lines1_1 = (
            'date,src,dest,amount\n'
            '2015/01/10,asset.checking,expense.food,-10\n'
            '2015/01/10,asset.checking,expense.duplicate,-20\n')

        # This food transaction should register as duplicate...
        lines1_2 = (
            'date,src,dest,amount\n'
            '2015/01/14,asset.checking,expense.food,-10\n')

        # But not in ledger2.
        lines2 = (
            'date,src,dest,amount\n'
            '2015/01/14,asset.checking,expense.food,-10\n'
            '2015/01/17,asset.investment,asset.checking,-10\n'
            '2015/01/10,asset.checking,expense.duplicate,-20\n')

        ledger1.load(lines1_1, 'p1')
        ledger1.load(lines1_2, 'p2')
        ledger2.load(lines2)

        self.assertEqual(2, len(ledger1.transactions))
        self.assertEqual(3, len(ledger2.transactions))

        ledger2.load(ledger1.dump())
        ledger1.load(ledger2.dump())

        # That duplicate food transaction should now appear in both dumps
        # because empty perspectives can only dupe on exact dates of an
        # original transaction.
        exp = Ledger(pcurr)
        lines = (
            'date,src,dest,amount\n'
            '2015/01/10,asset.checking,expense.food,-10\n'
            '2015/01/14,asset.checking,expense.food,-10\n'
            '2015/01/17,asset.investment,asset.checking,-10\n'
            '2015/01/10,asset.checking,expense.duplicate,-20\n')
        exp.load(lines)

        self.assertEqual(4, len(exp.transactions))
        self.assertEqual(4, len(ledger1.transactions))
        self.assertEqual(len(ledger1.transactions), len(ledger2.transactions))
        for t in exp.transactions:
            self.assertIn(t, ledger1.transactions)
            self.assertIn(t, ledger2.transactions)

    def test_overloading_empty_perspectives(self):
        """ Transactions from empty perspectives should "fill in".

        eg. If 5 identical transactions are empty but in the same report, then
        it should take 6 identical empty transactions to create a new entry.
        """
        ledger = Ledger(pcurr)
        lines = (
            'date,src,dest,amount\n'
            '11/11/11,asset.checking,expense.food,-10\n'
            '11/11/11,asset.checking,expense.food,-10\n'
            '11/11/11,asset.checking,expense.food,-10\n'
            '11/11/11,asset.checking,expense.food,-10\n')

        ledger.load(lines)
        ledger.load(lines)
        ledger.load(lines)

        self.assertEqual(4, len(ledger.transactions))

        lines += '11/11/11,asset.checking,expense.food,-10\n'
        ledger.load(lines)
        self.assertEqual(5, len(ledger.transactions))

        checking = ledger.accounts['asset.checking']
        food = ledger.accounts['expense.food']
        self.assertEqual(-50, checking.balances['usd'])
        self.assertEqual(50, food.balances['usd'])

    def test_empty_perspective_duplicate_same_date(self):
        """ Empty perspectives should only be considered duplicates if their
            dates exactly match the date of an original transaction.
        """
        ledger = Ledger(pcurr, duplicate_window=4)
        og = (
            'date,dest,amount\n'
            '09/10/2014,expense.food,-10\n')
        dupe = (
            'date,dest,amount\n'
            '09/14/2014,asset.checking,10\n')

        empty = (
            'date,src,dest,amount\n'
            '09/14/2014,asset.checking,expense.food,-10\n')

        og = ledger.load(og, thisname='asset.checking')
        dupe = ledger.load(dupe, thisname='expense.food')
        empty = ledger.load(empty)

        self.assertEqual(2, len(ledger.transactions))

        self.assertEqual(0, len(ledger.reportDupes(og)))
        self.assertEqual(1, len(ledger.reportDupes(dupe)))
        self.assertEqual(0, len(ledger.reportDupes(empty)))

    def test_empty_perspective_duplicate_same_date2(self):
        """ Same as above, but all perspectives are empty.
        """
        ledger = Ledger(pcurr, duplicate_window=5)
        t1 = (
            'date,src,dest,amount\n'
            '2009/10/10,asset.checking,expense.food,-10\n')
        t2 = (
            'date,src,dest,amount\n'
            '2009/10/10,asset.checking,expense.food,-10\n')

        # Should count as unique
        t3 = (
            'date,src,dest,amount\n'
            '2009/10/15,asset.checking,expense.food,-10\n')

        t1 = ledger.load(t1)
        t2 = ledger.load(t2)
        t3 = ledger.load(t3)

        self.assertEqual(2, len(ledger.transactions))

        self.assertEqual(0, len(ledger.reportDupes(t1)))
        self.assertEqual(1, len(ledger.reportDupes(t2)))
        self.assertEqual(0, len(ledger.reportDupes(t3)))

    def test_equivalent_transaction_same_perspective(self):
        """ Equal transactions from the same perspective should be inserted.

        Only applies to non-empty perspectives.
        """
        ledger = Ledger(pcurr)
        lines = (
            'date,dest,amount\n'
            '11/11/11,expense.video-games,-10\n')
        lines2 = (
            'date,dest,amount\n'
            '11/11/12,expense.video-games,-20\n')

        t = ledger.load(lines, thisname='asset.checking')
        t += ledger.load(lines, thisname='asset.checking')
        t += ledger.load(lines2, thisname='asset.checking')
        checking = ledger.accounts['asset.checking']

        self.assertEqual([], ledger.reportDupes(t))
        self.assertEqual(3, len(ledger.transactions))
        self.assertEqual(-40, checking.balances[pcurr])

    def test_equivalent_transaction_different_perspective(self):
        """ Equivalent transactions from the different files should be
            counted as duplicates.
        """
        ledger = Ledger(pcurr)
        t_checking = (
            'date,dest,amount\n'
            '11/11/11,asset.investment,-10\n')

        t_investment = (
            'date,dest,amount\n'
            '11/11/11,asset.checking,10\n')

        trans = ledger.load(t_checking, thisname='asset.checking')
        trans += ledger.load(t_investment, thisname='asset.investment')

        checking = ledger.accounts['asset.checking']
        investment = ledger.accounts['asset.investment']

        dupes = ledger.reportDupes(trans)
        t, o, a = dupes[0]
        self.assertEqual(1, len(dupes))
        self.assertIs(trans[1], t)
        self.assertEqual('asset.checking', o)
        self.assertEqual('asset.investment', a)

        self.assertEqual(1, len(ledger.transactions))
        self.assertEqual(-10, checking.balances[pcurr])
        self.assertEqual(10, investment.balances[pcurr])

    def test_real_perspective_dupes_empty_perspective(self):
        """ Regular perspectives should duplicate empties just the same.
        """
        ledger = Ledger(pcurr, duplicate_window=5)
        t1 = (
            'date,src,dest,amount\n'
            '2011/11/11,asset.checking,expense.food,-10\n')

        t2 = (
            'date,src,dest,amount\n'
            '2011/11/15,asset.checking,expense.food,-10\n')

        ledger.load(t1)
        t = ledger.load(t2, thisname='asset.checking')

        self.assertEqual(1, len(ledger.transactions))

        dupes = ledger.reportDupes(t)
        self.assertEqual(1, len(dupes))

        t, o, a = dupes[0]
        self.assertEqual(o, '')
        self.assertEqual(a, 'asset.checking')

    def test_2_dates_over_5_perspectives(self):
        """ 2 dates over 5 perspectives should produce 1 transaction.
        """
        ledger = Ledger(pcurr, duplicate_window=2)
        header = 'date,src,dest,amount\n'

        t1 = '2011/11/11,asset.checking,expense.food,-10\n'
        t2 = '2011/11/12,asset.checking,expense.food,-10\n'
        t3 = '2011/11/11,asset.checking,expense.food,-10\n'
        t4 = '2011/11/12,asset.checking,expense.food,-10\n'
        t5 = '2011/11/11,asset.checking,expense.food,-10\n'

        t = ledger.load(header + t1, thisname='p1')
        t += ledger.load(header + t2, thisname='p2')
        t += ledger.load(header + t3, thisname='p3')
        t += ledger.load(header + t4, thisname='p4')
        t += ledger.load(header + t5, thisname='p5')

        dupes = ledger.reportDupes(t)

        self.assertEqual(1, len(ledger.transactions))
        self.assertEqual(4, len(dupes))

        self.assertIs(t[1], dupes[0][0])
        self.assertIs(t[2], dupes[1][0])
        self.assertIs(t[3], dupes[2][0])
        self.assertIs(t[4], dupes[3][0])

    def test_date_limit_on_dupes(self):
        """ 3 persepctives with 3 dates should produce 2 unique entires.

        This is because duplicate buckets can only support a maximum of
        2 unique dates. How could 3 dates relate to a single transaction?
        """
        ledger = Ledger(pcurr, duplicate_window=3)
        header = 'date,src,dest,amount\n'

        # These 2 should get paired.
        t1 = '01/01/2021,asset.checking,expense.food,-10\n'
        t2 = '01/02/2021,asset.checking,expense.food,-10\n'

        # This one should be unique.
        t3 = '01/03/2021,asset.checking,expense.food,-10\n'

        trans = ledger.load(header + t1, thisname='p1')
        trans += ledger.load(header + t2, thisname='p2')
        trans += ledger.load(header + t3, thisname='p3')

        checking = ledger.accounts['asset.checking']

        self.assertEqual(2, len(ledger.transactions))
        self.assertEqual(-20, checking.balances['usd'])

        dupes = ledger.reportDupes(trans)
        self.assertEqual(1, len(dupes))

        t, o, a = dupes[0]
        self.assertIs(trans[1], t)
        self.assertEqual('p1', o)
        self.assertEqual('p2', a)

    def test_duplicate_matching_src_and_dest(self):
        """ Duplicates should require matching src and dest accounts.
        """
        ledger = Ledger(pcurr, duplicate_window=5)

        # asset.checking records a $10 refund from expense.food
        t1 = (
            'date,dest,amount\n'
            '01/10/2021,expense.food,10\n')

        # asset.checking records a $10 expense to expense.food
        t2 = (
            'date,src,dest,amount\n'
            '01/10/2021,asset.checking,expense.food,-10\n')

        trans = ledger.load(t1, thisname='asset.checking')
        trans += ledger.load(t2, thisname='p2')

        dupes = ledger.reportDupes(trans)
        self.assertEqual([], dupes)
        self.assertEqual(2, len(ledger.transactions))

    def test_duplicate_window(self):
        """ Transactions should be unique if outside the window.
        """
        ledger = Ledger(pcurr, duplicate_window=5)
        header = 'date,src,dest,amount\n'

        # These should be 3 unique transactions.
        t1 = '01/10/2021,asset.checking,expense.food,-10\n'
        t2 = '01/04/2021,asset.checking,expense.food,-10\n'
        t3 = '01/16/2021,asset.checking,expense.food,-10\n'

        trans = ledger.load(header + t1, thisname='p1')
        trans += ledger.load(header + t2, thisname='p2')
        trans += ledger.load(header + t3, thisname='p3')

        dupes = ledger.reportDupes(trans)
        self.assertEqual([], dupes)

        self.assertEqual(3, len(ledger.transactions))

    def test_duplicate_window2(self):
        """ Transactions should be duplicates if inside the window.
        """
        ledger = Ledger(pcurr, duplicate_window=5)

        t1 = (
            'date,dest,amount\n'
            '01/10/2021,asset.investment,10\n'
            '01/10/2021,expense.food,-10\n')

        # These should be paired with those above.
        t2 = (
            'date,src,dest,amount\n'
            '01/05/2021,asset.investment,asset.checking,-10\n'
            '01/15/2021,asset.checking,expense.food,-10\n')

        trans = ledger.load(t1, thisname='asset.checking')
        trans += ledger.load(t2, thisname='p2')

        dupes = ledger.reportDupes(trans)
        self.assertEqual(2, len(dupes))
        for e, a in zip(trans[:2], ledger.transactions):
            self.assertIs(e, a)

        exp = [
            (trans[2], 'asset.checking', 'p2'),
            (trans[3], 'asset.checking', 'p2')]

        for e, a in zip(exp, dupes):
            t1, o1, a1 = e
            t2, o2, a2 = a

            self.assertIs(t1, t2)
            self.assertEqual(o1, o2)
            self.assertEqual(a1, a2)

    def test_duplicate_window3(self):
        """ Same as the previous 2, but change the window width.
        """
        ledger = Ledger(pcurr, duplicate_window=2)

        orig = (
            'date,src,dest,amount\n'
            '2021/01/10,asset.checking,asset.investment,-10\n')

        out = (
            'date,src,dest,amount\n'
            '2021/01/12 00:00:01,asset.checking,asset.investment,-10\n')

        # Should flag as duplicate.
        in_ = (
            'date,src,dest,amount\n'
            '2021/01/12,asset.checking,asset.investment,-10\n')

        t = ledger.load(orig, thisname='p1')
        t += ledger.load(out, thisname='p2')
        t += ledger.load(in_, thisname='p3')

        self.assertEqual(2, len(ledger.transactions))
        self.assertEqual(1, len(ledger.reportDupes(t)))

        # Expected transactions.
        lines = (
            'date,src,dest,amount\n'
            '2021/01/10,asset.checking,asset.investment,-10\n'
            '2021/01/12 00:00:01,asset.checking,asset.investment,-10\n')

        exp = Ledger(pcurr)
        exp.load(lines)

        for t in exp.transactions:
            self.assertIn(t, ledger.transactions)


if __name__ == '__main__':
    unittest.main()
