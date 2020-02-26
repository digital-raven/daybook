""" expense subcommand.
"""

import sys
from collections import defaultdict

import datetime
from prettytable import PrettyTable

from daybook.client import client
from daybook.client.dump import get_dump
from daybook.client.filtering import create_filter_func
from daybook.client.load import local_load
from daybook.Ledger import Ledger


def do_expense(args):
    """ Entry point for the expense subcommand.
    """
    # set start date for current month
    if not args.start and not args.end and not args.range:
        args.start = datetime.date.today()
        args.start = args.start.replace(day=1)
        args.start = str(args.start)

    if not args.types:
        args.types.extend(['expense', 'income'])

    # load the ledger
    if not args.csvs:
        try:
            server = client.open(args.hostname, args.port)
        except ConnectionRefusedError as e:
            print(e)
            sys.exit(1)

        ledger = Ledger(args.primary_currency)
        ledger.load(get_dump(server, args))
    else:
        filter_ = create_filter_func(args)
        ledger = local_load(args).filtered(filter_)

    # income table
    pt = PrettyTable()
    pt.field_names = ['Account', 'Balance']
    pt.align = 'l'
    for name in sorted([x for x in ledger.accounts if ledger.accounts[x].type == 'income']):
        account = ledger.accounts[name]
        balances = []
        for cur in sorted(account.balances):
            balance = account.balances[cur]
            balances.append('{}: {}'.format(cur, -balance))

        pt.add_row([name, '\n'.join(balances)])
    print('Income')
    print(pt, '\n')

    # expense table
    pt = PrettyTable()
    pt.field_names = ['Account', 'Balance']
    pt.align = 'l'
    for name in sorted([x for x in ledger.accounts if ledger.accounts[x].type == 'expense']):
        account = ledger.accounts[name]
        balances = []
        for cur in sorted(account.balances):
            balance = account.balances[cur]
            balances.append('{}: {}'.format(cur, balance))

        pt.add_row([name, '\n'.join(balances)])
    print('Expenses')
    print(pt, '\n')

    # total cash flow
    pt = PrettyTable()
    pt.field_names = ['Currency', 'Balance']
    pt.align = 'l'

    balances = defaultdict(lambda: 0)
    for name in sorted(ledger.accounts):
        account = ledger.accounts[name]
        if (account.type in ['expense', 'income']):
            for cur in account.balances:
                balance = account.balances[cur]
                balances[cur] -= balance

    for cur, balance in balances.items():
        pt.add_row([cur, balance])

    print('Cash flow')
    print(pt, '\n')
