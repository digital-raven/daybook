""" Entry point for the "dump" subcommand.

Dumps transactions from the server.
"""

import sys

from daybook.client.load import load_from_args


def main(args):
    """ Retrieve transactions from daybookd as a raw csv string.
    """
    try:
        ledger = load_from_args(args)
        print(ledger.dump())
    except (ConnectionRefusedError, FileNotFoundError, ValueError) as e:
        print(e)
        sys.exit(1)
