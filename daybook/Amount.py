""" Amount class
"""

import shlex


def _cast_list(l_):
    """ Casts the references in l_ to two lists - floats and strs.
    """
    floats = []
    strs = []
    for elem in l_:
        try:
            x = float(elem)
            floats.append(x)
        except ValueError:
            strs.append(elem)

    return floats, strs


class Amount:
    def __init__(self, src_currency, src_amount, dest_currency, dest_amount):

        try:
            src_amount = float(src_amount)
            dest_amount = float(dest_amount)
        except ValueError:
            raise ValueError('Could not convert amount entries to floats.')

        src_currency = src_currency
        dest_currency = dest_currency

        if src_amount * dest_amount > 0:
            raise ValueError('One side has to lose while the other gains.')

        if src_currency == dest_currency and src_amount != -dest_amount:
            raise ValueError('Uneven exchange: {} and {}.'.format(src_amount, dest_amount))

        if type(src_currency) is not str or type(dest_currency) is not str:
            raise ValueError('Currencies must be strings.')

        self.src_currency = src_currency
        self.src_amount = src_amount
        self.dest_currency = dest_currency
        self.dest_amount = dest_amount

    def __str__(self):
        return '{}:{} {}:{}'.format(
            self.src_currency,
            self.src_amount,
            self.dest_currency,
            self.dest_amount)

    def __eq__(self, other):
        return (
            self.src_currency == other.src_currency
            and self.src_amount == other.src_amount
            and self.dest_currency == other.dest_currency
            and self.dest_amount == other.dest_amount)

    @classmethod
    def createFromStr(cls, s, suggestion):
        """ Create amount from string.

        The line is tokenized and examined for the following formats.

        single
            10 => suggestion:10 suggestion:-10

        double
            10 usd => usd:10 usd:-10
            usd 10 => usd:10 usd:-10

        quadruple
            10 -20 usd mxn
            usd mxn 10 -20
            10 usd -20 mxn
            usd 10 mxn -20
            usd 10 -20 mxn
            usd 10 mxn -20

        Args:
            s: The string to parse.
            suggestion: Currency to use in case one couldn't be determined.

        Returns:
            New Amount instance.

        Raises:
            ValueError if the string couldn't be turned into a valid Amount.
        """

        scurr = None
        dcurr = None
        samount = None
        damount = None

        # scrub out colons and split into amounts and currencies.
        toks = s.replace(':', ' ').split()
        amounts, currencies = _cast_list(toks)

        # parse list
        if len(toks) == 1:
            try:
                samount = amounts[0]
            except IndexError:
                raise ValueError('No amount provided for exchange.')

            damount = -samount
            scurr = suggestion
            dcurr = scurr

        elif len(toks) == 2:
            try:
                samount = amounts[0]
            except IndexError:
                raise ValueError('No amount provided for exchange.')

            try:
                scurr = currencies[0]
            except IndexError:
                raise ValueError('No currency provided for exchange.')

            damount = -samount
            dcurr = scurr

        elif len(toks) == 4:
            try:
                samount = amounts[0]
                damount = amounts[1]
            except IndexError:
                raise ValueError('Not enough amounts specified.')

            try:
                scurr = currencies[0]
                dcurr = currencies[1]
            except IndexError:
                raise ValueError('Not enough currency types specified.')

        elif len(toks) == 3:
            raise ValueError('Odd "amount" entry - too many currencies or amounts.')
        elif not toks:
            raise ValueError('Empty string provided for amount.')
        else:
            raise ValueError('Invalid amount - too many entries')

        return Amount(scurr, samount, dcurr, damount)
