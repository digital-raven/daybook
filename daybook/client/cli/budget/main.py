""" budget subcommand.
"""

import sys
from collections import defaultdict

import yaml
from prettytable import PrettyTable

from daybook.client.load import load_from_args
from daybook.Account import Account


def load_budgets(files):
    """ Load budgets from a list of files.

    The files must begin with a yaml block of data beginning with a '---',
    but may contain other notes after the yaml. Useful for writing down
    what motivated your budget. This also allows the budget files to be
    in an arbitrary file format.

    Multiple budgets may be provided and the values assigned to each account
    will be added to each other.

    eg...

        ---
        budget:
          income.myjob: -5000
          expense.grocery: 300
          liability.mortgage: 1000
          expense.computer: 1500
        ---

        ## Notes
        I've decided to spend 1500 on a gaming PC this month.

    Args:
        files: yaml files to load budgets from. Keys are account names
            and values are dollars assigned to each.

    Returns:
        A yaml dictionary representing the budget.
    """

    # Load budgets. Should be a simple yaml dict load.
    budget = defaultdict(lambda: 0)
    for b in files:
        with open(b) as f:
            s = f.read().split('---')[1]
            d = yaml.safe_load(s)

        for k, v in d['budget'].items():
            budget[k] += v

    # {type}.misc is for transactions not categorized in the budgets.
    for type in Account.types:
        budget[f'{type}.misc'] = 0

    return budget


def main(args):
    """ Entry point for budget subcommand.
    """
    try:
        ledger = load_from_args(args)
    except (ConnectionRefusedError, FileNotFoundError, ValueError) as e:
        print(e)
        sys.exit(1)

    budget = load_budgets(args.budgets)

    deltas = defaultdict(lambda: 0)
    deltas.update(budget)
    unaccounted = {}

    # Compute differences
    for name in sorted(ledger.accounts):
        account = ledger.accounts[name]
        balance = account.balances[args.primary_currency]

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
    print(exp)
    print(act)
