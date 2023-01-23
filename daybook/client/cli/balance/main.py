""" balance subcommand.
"""

import sys

from prettytable import PrettyTable

from daybook.client.load import load_from_args


def main(args):
    """ Entry point for balance subcommand.
    """
    try:
        ledger = load_from_args(args)
    except (ConnectionRefusedError, FileNotFoundError, ValueError) as e:
        print(e)
        sys.exit(1)

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
