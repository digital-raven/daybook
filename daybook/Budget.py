""" Functions for loading budgets.
"""

from collections import defaultdict

import yaml

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
        A dictionary representing the budget.
    """

    # Load budgets. Should be a simple yaml dict load.
    budget = defaultdict(lambda: 0)
    for b in files:
        with open(b) as f:
            s = f.read().split('---')[1]
            d = yaml.safe_load(s)

        if 'budget' in d:
            d = d['budget']

        for k, v in d.items():
            budget[k] += v

    # {type}.misc is for transactions not categorized in the budgets.
    for type in Account.types:
        budget[f'{type}.misc'] = 0

    return budget
