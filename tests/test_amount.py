import unittest

from daybook.Amount import Amount


class TestAmount(unittest.TestCase):
    """ Primarily concerned with the createFromStr method.
    """

    def test_empty(self):
        """ Empty string should raise ValueError.
        """
        with self.assertRaises(ValueError):
            Amount.createFromStr('', 'usd', 'usd')

    def test_blank(self):
        """ blank string should raise ValueError.
        """
        with self.assertRaises(ValueError):
            Amount.createFromStr(' ', 'usd', 'usd')

    def test_single_colon(self):
        """ A single colon should also raise.
        """
        with self.assertRaises(ValueError):
            Amount.createFromStr(':', 'usd', 'usd')

    def test_multi_colon(self):
        """ A multiple colons should also raise.
        """
        with self.assertRaises(ValueError):
            Amount.createFromStr(': :', 'usd', 'usd')

    def test_none_src_suggestion(self):
        """ src_currency = None should raise ValueError.
        """
        with self.assertRaises(ValueError):
            Amount.createFromStr('10', None, 'usd')

    def test_none_dest_suggestion(self):
        """ Verify cases where dest_currency is None.
        """
        with self.assertRaises(ValueError):
            Amount.createFromStr('usd:10 20', 'usd', None)

    def test_single_val(self):
        """ A single numeric value should be valid.

        And also result in each side of the Amount using the same
        currency - the src suggestion.
        """
        a = Amount.createFromStr('10', 'usd', 'mxn')
        self.assertEqual('usd', a.src_currency)
        self.assertEqual('usd', a.dest_currency)
        self.assertEqual(10, a.src_amount)
        self.assertEqual(10, a.dest_amount)

    def test_double_val(self):
        """ A double numeric value should rely on currency suggestions.
        """
        a = Amount.createFromStr('10 20', 'usd', 'mxn')
        self.assertEqual('usd', a.src_currency)
        self.assertEqual('mxn', a.dest_currency)
        self.assertEqual(10, a.src_amount)
        self.assertEqual(20, a.dest_amount)

    def test_single_negative(self):
        """ Negative numbers should be handled.

        And also result in each side of the Amount using the same
        currency - the src suggestion.
        """
        a = Amount.createFromStr('-10', 'usd', 'mxn')
        self.assertEqual('usd', a.src_currency)
        self.assertEqual('usd', a.dest_currency)
        self.assertEqual(10, a.src_amount)
        self.assertEqual(10, a.dest_amount)

    def test_single_val_trim(self):
        """ Preceeding and succeeding spaces should not matter.
        """
        a = Amount.createFromStr(' 10 ', 'usd', 'mxn')
        self.assertEqual('usd', a.src_currency)
        self.assertEqual('usd', a.dest_currency)
        self.assertEqual(10, a.src_amount)
        self.assertEqual(10, a.dest_amount)

    def test_spaced_value_currency(self):
        """ Something like '10 usd' should be valid.
        """
        a = Amount.createFromStr('10 usd', 'mxn', 'mxn')
        self.assertEqual('usd', a.src_currency)
        self.assertEqual('usd', a.dest_currency)
        self.assertEqual(10, a.src_amount)
        self.assertEqual(10, a.dest_amount)

    def test_src_currency(self):
        """ If a currency is specified then each side should use it.
        """
        a = Amount.createFromStr('usd:10', 'mxn', 'jpy')
        self.assertEqual('usd', a.src_currency)
        self.assertEqual('usd', a.dest_currency)
        self.assertEqual(10, a.src_amount)
        self.assertEqual(10, a.dest_amount)

    def test_two_currencies_one_amount(self):
        """ If competing currencies are provided, then 2 amounts are required.
        """
        with self.assertRaises(ValueError):
            a = Amount.createFromStr('usd:10 mxn', 'usd', 'mxn')

    def test_two_currencies_one_amount_2(self):
        """ Same as above but only the src currency is provided.
        """
        with self.assertRaises(ValueError):
            a = Amount.createFromStr('usd mxn:20', 'usd', 'mxn')

    def test_missing_dest_currency(self):
        """ A missing dest currency should use its suggestion.
        """
        a = Amount.createFromStr('usd:10 20', 'jpy', 'mxn')
        self.assertEqual('usd', a.src_currency)
        self.assertEqual('mxn', a.dest_currency)
        self.assertEqual(10, a.src_amount)
        self.assertEqual(20, a.dest_amount)

    def test_missing_src_currency(self):
        """ A missing src currency should use its suggestion.
        """
        a = Amount.createFromStr('10 20 mxn', 'jpy', 'usd')
        self.assertEqual('jpy', a.src_currency)
        self.assertEqual('mxn', a.dest_currency)
        self.assertEqual(10, a.src_amount)
        self.assertEqual(20, a.dest_amount)

    def test_colon_grouping_src(self):
        """ Colons should group src.
        """
        a = Amount.createFromStr('10:usd 20', 'jpy', 'jam')
        b = Amount.createFromStr('usd:10 20', 'jpy', 'jam')
        self.assertEqual('usd', a.src_currency)
        self.assertEqual('jam', a.dest_currency)
        self.assertEqual(10, a.src_amount)
        self.assertEqual(20, a.dest_amount)
        self.assertEqual(a, b)

    def test_colon_grouping_dest(self):
        """ Colons should group dest.
        """
        a = Amount.createFromStr('10 mxn:20', 'jpy', 'jam')
        b = Amount.createFromStr('10 20:mxn', 'jpy', 'jam')
        self.assertEqual('jpy', a.src_currency)
        self.assertEqual('mxn', a.dest_currency)
        self.assertEqual(10, a.src_amount)
        self.assertEqual(20, a.dest_amount)
        self.assertEqual(a, b)

    def test_colon_grouping_both(self):
        """ Colons should group currencies with amounts.
        """
        a = Amount.createFromStr('10:usd mxn:20', 'jpy', 'jam')
        b = Amount.createFromStr('usd:10 20:mxn', 'jpy', 'jam')
        self.assertEqual('usd', a.src_currency)
        self.assertEqual('mxn', a.dest_currency)
        self.assertEqual(10, a.src_amount)
        self.assertEqual(20, a.dest_amount)
        self.assertEqual(a, b)

    def test_colon_invalid_group(self):
        """ Groups should have both an amount and currency.
        """
        with self.assertRaises(ValueError):
            Amount.createFromStr('10:100', 'mxn', 'jpy')
        with self.assertRaises(ValueError):
            Amount.createFromStr('usd:mxn', 'mxn', 'jpy')
        with self.assertRaises(ValueError):
            Amount.createFromStr('10 usd:mxn', 'mxn', 'jpy')
        with self.assertRaises(ValueError):
            Amount.createFromStr('10 usd:mxn', 'mxn', 'jpy')

    def test_middle_colon(self):
        """ Middle colons should raise.
        """
        with self.assertRaises(ValueError):
            Amount.createFromStr('10:mxn:usd:100', 'mxn', 'jpy')

    def test_full_conversion(self):
        """ Verify acceptance of fully-specified exchange.
        """
        a = Amount.createFromStr('usd:10 mxn:20', 'jpy', 'yomamma')
        b = Amount.createFromStr('usd 10 mxn 20', 'jpy', 'yomamma')
        self.assertEqual('usd', a.src_currency)
        self.assertEqual('mxn', a.dest_currency)
        self.assertEqual(10, a.src_amount)
        self.assertEqual(20, a.dest_amount)
        self.assertEqual(a, b)

    def test_full_conversion_2(self):
        """ Verify acceptance of fully-specified exchange.
        """
        a = Amount.createFromStr('usd 10  20 mxn', 'jpy', 'genji')
        self.assertEqual('usd', a.src_currency)
        self.assertEqual('mxn', a.dest_currency)
        self.assertEqual(10, a.src_amount)
        self.assertEqual(20, a.dest_amount)

    def test_too_many_amounts_3(self):
        """ 3 amounts should raise.
        """
        with self.assertRaises(ValueError):
            Amount.createFromStr('20  10 100', 'mxn', 'jpy')

    def test_too_many_amounts_4(self):
        """ 4 amounts should raise.
        """
        with self.assertRaises(ValueError):
            Amount.createFromStr('20  10 100 20', 'mxn', 'jpy')

    def test_too_many_currencies_1(self):
        """ 1 currency should raise.
        """
        with self.assertRaises(ValueError):
            Amount.createFromStr('usd', 'mxn', 'jpy')

    def test_too_many_currencies_2(self):
        """ 2 currencies should raise.
        """
        with self.assertRaises(ValueError):
            Amount.createFromStr('usd mxn', 'mxn', 'jpy')

    def test_too_many_currencies_3(self):
        """ 3 currencies should raise.
        """
        with self.assertRaises(ValueError):
            Amount.createFromStr('usd mxn jpy', 'mxn', 'jpy')

    def test_too_many_currencies_4(self):
        """ 4 currencies should raise.
        """
        with self.assertRaises(ValueError):
            Amount.createFromStr('usd mxn jpy jam', 'mxn', 'jpy')

    def test_competing_amounts(self):
        """ Identical currencies should require identical amounts.
        """
        with self.assertRaises(ValueError):
            Amount.createFromStr('usd:10 usd:100', 'mxn', 'jpy')

    def test_abs(self):
        """ Absolute values should be used for both sides.
        """
        a = Amount.createFromStr('-100', 'mxn', 'jpy')
        self.assertEqual(100, a.src_amount)
        self.assertEqual(100, a.dest_amount)


if __name__ == '__main__':
    unittest.main()
