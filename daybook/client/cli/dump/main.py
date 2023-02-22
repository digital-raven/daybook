""" Entry point for the "dump" subcommand.
"""

import sys

from daybook.client.load import load_from_args


def main(args):
    """ Print transactions as a raw csv string to stdout.
    """
    try:
        ledger = load_from_args(args)
        print(ledger.dump())
    except (FileNotFoundError, ValueError) as e:
        print(e)
        sys.exit(1)
