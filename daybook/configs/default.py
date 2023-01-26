import random
import string
from pathlib import Path


default_ini = '''\
# This file will be copied to $HOME/.config/daybook on the first run.

[default]

# Default location to search for CSVs. If this isn't specified, then
# $HOME/.local/share/daybook is used.
# The hints.ini should be at the root of this directory too.
ledger_root = __LEDGER_ROOT

# Default primary currency for accounts.
primary_currency = usd

# host and port of server. If not specified when running daybook for the
# first time, then localhost will be used for the hostname, and a random number
# between 5000 and 15000 will be selected for the server.
hostname = localhost
port = __PORT

# username and password for connecting to daybookd.
# These will be set to random strings within $HOME/.config/daybook/config.ini
# the first time daybook is run for your user.
username = __USERNAME
password = __PASSWORD

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
    charset = string.ascii_lowercase + string.ascii_uppercase + string.digits

    ledger_root = f'{Path.home()}/.local/share/daybook'
    port = random.randint(5000, 15000)
    username = ''.join(random.SystemRandom().choice(charset) for _ in range(20))
    password = ''.join(random.SystemRandom().choice(charset) for _ in range(20))

    s = default_ini
    s = s.replace('__LEDGER_ROOT', ledger_root)
    s = s.replace('__PORT', str(port))
    s = s.replace('__USERNAME', username)
    s = s.replace('__PASSWORD', password)

    return s
