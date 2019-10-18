""" Amount class
"""

import shlex

def exception_counter(l_, func):
    """ Returns how many elements of l_ raised in func.
    """
    i = 0
    for elem in l_:
        try:
            func(elem)
        except Exception as e:
            i = i + 1
    return i

class Amount:
    def __init__(self, src_currency, src_amount, dest_currency, dest_amount):

        src_amount = abs(src_amount)
        dest_amount = abs(dest_amount)

        src_currency = src_currency.strip()
        dest_currency = dest_currency.strip()

        if src_currency == dest_currency and not src_amount == dest_amount:
            raise ValueError('Uneven exchange.')

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
    def _createFromStrHelper(cls, s):
        src = [x for x in s.split(':') if x]
        if not exception_counter(src, lambda x: float(x)) == 1:
            raise ValueError('Invalid grouping')

        if len(src) == 1:
            currency = ''
            amount = float(src[0])
        elif len(src) == 2:
            try:
                currency = src[0]
                amount = float(src[1])
            except ValueError:
                try:
                    amount = float(src[0])
                    currency = src[1]
                except ValueError:
                    raise ValueError('No amount provided in group')
        else:
            raise ValueError('Currencies cannot contain colons.')

        return currency, amount

    @classmethod
    def createFromStr(cls, s, suggested_src, suggested_dest):
        """ Create amount from string and suggested src and dest accounts.

        The accounts are there to 'fill in the blanks' in case a src
        or destination currency is not specified in s.

        The line is tokenized and examined for the following formats.

        single
            10 => valid => src:10 dest:10

        double
            10 dollar => valid => dollar:10 dollar:10
            dollar 10 => valid => dollar:10 dollar:10
            10 20 => valid => src:10 dest:20

        triple
            dollar 10 20 => valid => dollar:10 dest:20
            10 20 dollar => valid => src:10 dollar:20

        quadruple
            10 20 dollar peso => valid
            dollar peso 10 20 => valid
            10 dollar 20 peso => valid
            dollar 10 peso 20 => valid
            dollar 10 20 peso => valid
            dollar 10 peso 20 => valid
        """

        scurr = None
        dcurr = None
        samount = None
        damount = None

        if type(suggested_src) is not str or type(suggested_dest) is not str:
            raise ValueError('Currencies must be strings.')

        # split into non-blank tokens
        toks = shlex.split(s)

        # scrub out colons
        ntoks = []
        for tok in toks:
            if ':' in tok:
                c, a = Amount._createFromStrHelper(tok)
                if ntoks:
                    ntoks.extend([a, c])
                else:
                    ntoks.extend([c, a])
            else:
                ntoks.append(tok)
        toks = ntoks

        # parse list
        if len(toks) == 1:
            try:
                samount = float(toks[0])
            except ValueError:
                raise ValueError('No amounts provided for exchange')

            damount = samount
            scurr = suggested_src
            dcurr = suggested_src
        elif len(toks) == 2:
            try:
                samount = float(toks[0])
                damount = float(toks[1])
                scurr = suggested_src
                dcurr = suggested_dest
            except ValueError:
                try:
                    samount = float(toks[0])
                    scurr = toks[1]
                    damount = samount
                    dcurr = scurr
                except ValueError:
                    try:
                        scurr = toks[0]
                        samount = float(toks[1])
                        damount = samount
                        dcurr = scurr
                    except ValueError:
                        raise ValueError('No amounts provided for exchange')
        elif len(toks) == 3:

            nex = exception_counter(toks, lambda x: float(x))
            if not nex == 1:
                raise ValueError('Too many currencies provided')

            try:
                samount = float(toks[0])
                damount = float(toks[1])
                dcurr = toks[2]
                scurr = suggested_src
            except ValueError:
                try:
                    scurr = toks[0]
                    samount = float(toks[1])
                    damount = float(toks[2])
                    dcurr = suggested_dest
                except ValueError:
                    raise ValueError('This was a bad')
        elif len(toks) == 4:
            nex = exception_counter(toks, lambda x: float(x))
            if not nex == 2:
                raise ValueError('Too many currencies provided')

            amounts = []
            currencies = []

            for tok in toks:
                try:
                    x = float(tok)
                    amounts.append(x)
                except ValueError:
                    currencies.append(tok)

            samount = amounts[0]
            damount = amounts[1]
            scurr = currencies[0]
            dcurr = currencies[1]
        else:
            raise ValueError('Invalid amount - too many entries')

        return Amount(scurr, samount, dcurr, damount)
