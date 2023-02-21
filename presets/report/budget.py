import sys
from collections import defaultdict

from prettytable import PrettyTable


help = 'Budget report'

description = '''
Print a budget vs the actual expenses.
'''


def report(ledger, budget):
    """ Basic budget report.
    """
    deltas = defaultdict(lambda: 0)
    deltas.update(budget)
    unaccounted = {}

    # Compute differences
    for name in sorted(ledger.accounts):
        account = ledger.accounts[name]
        balance = account.balances[ledger.primary_currency]

        deltas[account.name] += balance

    # Expected budget table
    exp = PrettyTable()
    exp.field_names = ['Account', 'Expected Balance']
    exp.align['Account'] = 'l'
    exp.align['Expected Balance'] = 'r'
    misc_rows = []
    for account in sorted(budget):
        if not account.endswith('.misc'):
            exp.add_row([account, budget[account]])
        else:
            misc_rows.append([account, budget[account]])

    exp.add_row(['', ''])
    exp.add_rows(misc_rows)

    # Deltas table
    misc = {}
    act = PrettyTable()
    act.field_names = ['Account', 'Difference']
    act.align['Account'] = 'l'
    act.align['Difference'] = 'r'
    misc_rows = []
    for account in sorted(deltas):
        if not account.endswith('.misc'):
            act.add_row([account, budget[account]])
        else:
            misc_rows.append([account, budget[account]])

    act.add_row(['', ''])
    act.add_rows(misc_rows)

    # Print tables
    return ''.join([str(exp), '\n', str(act)])
