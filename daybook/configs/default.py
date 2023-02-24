from pathlib import Path


default_ini = '''\
# This file will be copied to $HOME/.config/daybook on the first run.

[default]

# Default primary currency for accounts.
primary_currency = usd

# For duplicate checking. Transactions loaded from different CSVs that are
# identical in source account, destination account, amount, and are within
# the day range specified by this parameter will be deemed as duplicates and
# will not be loaded into the ledger's transactions.
#
# If duplicate checking is not desired, set this value to "off". If duplicate
# checking is desired only for exact dates, then set this value to 0.
duplicate_window = 5
'''


def create_default_ini():
    """ Return the default ini with Substituted values.
    """
    return default_ini
