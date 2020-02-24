""" balance subcommand.
"""

import sys

from prettytable import PrettyTable

from daybook.client import client
from daybook.client.dump import get_dump
from daybook.client.load import local_load
from daybook.Ledger import Ledger


def do_balance(args):
    """ Entry point for balance subcommand.
    """

    try:
        server = client.open(args.hostname, args.port)
    except ConnectionRefusedError as e:
        print(e)
        sys.exit(1)

    ledger = Ledger(args.primary_currency)
    ledger.load(get_dump(server, args))

    # balance table
    pt = PrettyTable()
    pt.field_names = ['Account', 'Balance']
    pt.align['Account'] = 'l'
    pt.align['Balance'] = 'r'
    for name in sorted(ledger.accounts):
        account = ledger.accounts[name]
        balances = []
        for cur in sorted(account.balances):
            balance = account.balances[cur]
            balances.append('{}: {}'.format(cur, round(balance, 2)))

        pt.add_row([name, '\n'.join(balances)])

    print(pt, '\n')
