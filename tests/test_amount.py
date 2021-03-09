import unittest

from daybook.Amount import Amount


class TestAmount(unittest.TestCase):
    """ Primarily concerned with the createFromStr method.
    """

    def test_empty(self):
        """ Empty string should raise ValueError.
        """
        with self.assertRaises(ValueError):
            Amount.createFromStr('', 'usd')

    def test_blank(self):
        """ blank string should raise ValueError.
        """
        with self.assertRaises(ValueError):
            Amount.createFromStr(' ', 'usd')

    def test_single_colon(self):
        """ A single colon should also raise.
        """
        with self.assertRaises(ValueError):
            Amount.createFromStr(':', 'usd')

    def test_multi_colon(self):
        """ A multiple colons should also raise.
        """
        with self.assertRaises(ValueError):
            Amount.createFromStr(': :', 'usd')

    def test_none_src_suggestion(self):
        """ src_currency = None should raise ValueError.
        """
        with self.assertRaises(ValueError):
            Amount.createFromStr('10', None)

    def test_single_val(self):
        """ A single numeric value should be valid.

        And also result in each side of the Amount using the same
        currency - the src suggestion.
        """
        a = Amount.createFromStr('10', 'mxn')
        self.assertEqual('mxn', a.src_currency)
        self.assertEqual('mxn', a.dest_currency)
        self.assertEqual(10, a.src_amount)
        self.assertEqual(-10, a.dest_amount)

    def test_single_negative(self):
        """ Negative numbers should be handled.

        And also result in each side of the Amount using the same
        currency - the src suggestion.
        """
        a = Amount.createFromStr('-10', 'usd')
        self.assertEqual('usd', a.src_currency)
        self.assertEqual('usd', a.dest_currency)
        self.assertEqual(-10, a.src_amount)
        self.assertEqual(10, a.dest_amount)

    def test_single_val_trim(self):
        """ Preceeding and succeeding spaces should not matter.
        """
        a = Amount.createFromStr(' 10 ', 'usd')
        self.assertEqual('usd', a.src_currency)
        self.assertEqual('usd', a.dest_currency)
        self.assertEqual(10, a.src_amount)
        self.assertEqual(-10, a.dest_amount)

    def test_spaced_value_currency(self):
        """ Something like '10 usd' should be valid.
        """
        a = Amount.createFromStr('10 usd', 'mxn')
        self.assertEqual('usd', a.src_currency)
        self.assertEqual('usd', a.dest_currency)
        self.assertEqual(10, a.src_amount)
        self.assertEqual(-10, a.dest_amount)

    def test_src_currency(self):
        """ If a currency is specified then each side should use it.
        """
        a = Amount.createFromStr('usd:10', 'mxn')
        self.assertEqual('usd', a.src_currency)
        self.assertEqual('usd', a.dest_currency)
        self.assertEqual(10, a.src_amount)
        self.assertEqual(-10, a.dest_amount)

    def test_two_currencies_one_amount(self):
        """ If competing currencies are provided, then 2 amounts are required.
        """
        with self.assertRaises(ValueError):
            a = Amount.createFromStr('usd:10 mxn', 'usd')

    def test_two_currencies_one_amount_2(self):
        """ Same as above but only the src currency is provided.
        """
        with self.assertRaises(ValueError):
            a = Amount.createFromStr('usd mxn:20', 'usd')

    def test_missing_dest_currency(self):
        """ 2 vals with one currency should raise.
        """
        with self.assertRaises(ValueError):
            a = Amount.createFromStr('usd:10 20', 'jpy')

    def test_missing_src_currency(self):
        """ This configuration should raise as well.
        """
        with self.assertRaises(ValueError):
            a = Amount.createFromStr('10 20 mxn', 'jpy')

    def test_full_conversion(self):
        """ Verify acceptance of fully-specified exchange.
        """
        a = Amount.createFromStr('usd:-10 mxn:20', 'jpy')
        b = Amount.createFromStr('usd -10 mxn 20', 'jpy')
        self.assertEqual('usd', a.src_currency)
        self.assertEqual('mxn', a.dest_currency)
        self.assertEqual(-10, a.src_amount)
        self.assertEqual(20, a.dest_amount)
        self.assertEqual(a, b)

    def test_full_conversion_2(self):
        """ Verify acceptance of fully-specified exchange.
        """
        a = Amount.createFromStr('usd -10  20 mxn', 'jpy')
        self.assertEqual('usd', a.src_currency)
        self.assertEqual('mxn', a.dest_currency)
        self.assertEqual(-10, a.src_amount)
        self.assertEqual(20, a.dest_amount)

    def test_full_conversion_3(self):
        """ Verify acceptance of fully-specified exchange.
        """
        a = Amount.createFromStr('usd -10  20 mxn', 'jpy')
        self.assertEqual('usd', a.src_currency)
        self.assertEqual('mxn', a.dest_currency)
        self.assertEqual(-10, a.src_amount)
        self.assertEqual(20, a.dest_amount)

    def test_double_val(self):
        """ A double numeric value should raise.
        """
        with self.assertRaises(ValueError):
            a = Amount.createFromStr('10 20', 'usd')

    def test_double_val_2(self):
        """ 2 vals and one currency should raise.
        """
        with self.assertRaises(ValueError):
            Amount.createFromStr('usd:10 20', 'usd')

    def test_full_conversion_4(self):
        """ Swap the sign for good measure.
        """
        a = Amount.createFromStr('usd 10  -20 mxn', 'jpy')
        self.assertEqual('usd', a.src_currency)
        self.assertEqual('mxn', a.dest_currency)
        self.assertEqual(10, a.src_amount)
        self.assertEqual(-20, a.dest_amount)

    def test_too_many_amounts_3(self):
        """ 3 amounts should raise.
        """
        with self.assertRaises(ValueError):
            Amount.createFromStr('20  10 100', 'mxn')

    def test_too_many_amounts_4(self):
        """ 4 amounts should raise.
        """
        with self.assertRaises(ValueError):
            Amount.createFromStr('20  10 100 20', 'mxn')

    def test_too_many_currencies_1(self):
        """ 1 currency should raise.
        """
        with self.assertRaises(ValueError):
            Amount.createFromStr('usd', 'mxn')

    def test_too_many_currencies_2(self):
        """ 2 currencies should raise.
        """
        with self.assertRaises(ValueError):
            Amount.createFromStr('usd mxn', 'mxn')

    def test_too_many_currencies_3(self):
        """ 3 currencies should raise.
        """
        with self.assertRaises(ValueError):
            Amount.createFromStr('usd mxn jpy', 'mxn')

    def test_too_many_currencies_4(self):
        """ 4 currencies should raise.
        """
        with self.assertRaises(ValueError):
            Amount.createFromStr('usd mxn jpy jam', 'mxn')

    def test_competing_amounts(self):
        """ Identical currencies should require balanced amounts.
        """
        with self.assertRaises(ValueError):
            Amount.createFromStr('usd:10 usd:-10.1', 'mxn')

    def test_identical_amounts(self):
        """ Both amounts need to have the same sign.
        """
        with self.assertRaises(ValueError):
            Amount.createFromStr('usd:10 mxn:10.1', 'mxn')

        with self.assertRaises(ValueError):
            Amount.createFromStr('usd:-10 mxn:-10.1', 'mxn')

    def test_negative_zero(self):
        """ ... unless we're dealing with -0. This shouldn't raise.
        """
        a = Amount.createFromStr('usd:-0.00 mxn:-0.00', 'mxn')
        a = Amount.createFromStr('usd:0.00 mxn:0.00', 'mxn')

    def test_correction(self):
        """ Amount.correct should swap src and dest if src_amount is negative.

        The constructor should just accept at face value, however.
        """

        # This should be fine
        a = Amount.createFromStr('-1.0 usd mxn 1', 'usd')
        self.assertEqual('usd', a.src_currency)
        self.assertEqual('mxn', a.dest_currency)
        self.assertEqual(-1, a.src_amount)
        self.assertEqual(1, a.dest_amount)

        a.correct()
        self.assertEqual('usd', a.src_currency)
        self.assertEqual('mxn', a.dest_currency)
        self.assertEqual(-1, a.src_amount)
        self.assertEqual(1, a.dest_amount)

        # This should be corrected
        a = Amount.createFromStr('1 usd mxn -1', 'usd')
        self.assertEqual('usd', a.src_currency)
        self.assertEqual('mxn', a.dest_currency)
        self.assertEqual(1, a.src_amount)
        self.assertEqual(-1, a.dest_amount)

        a.correct()
        self.assertEqual('mxn', a.src_currency)
        self.assertEqual('usd', a.dest_currency)
        self.assertEqual(-1, a.src_amount)
        self.assertEqual(1, a.dest_amount)


if __name__ == '__main__':
    unittest.main()
