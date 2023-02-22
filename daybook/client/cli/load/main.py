""" Entry point for the load subcommand.
"""

import sys

from daybook.client import client
from daybook.client.load import load_from_args


def main(args):
    """ Load a local ledger with CSVs and send to daybookd.
    """
    if not args.csvs:
        args.csvs = args.ledger_root

    if not args.hostname or not args.port:
        print('ERROR: No hostname or port specified.')
        sys.exit(1)

    try:
        int(args.port)
    except ValueError:
        print('ERROR: Port "{}" is not an integer.'.format(args.port))
        sys.exit(1)

    try:
        server = client.open(args.hostname, args.port)
        ledger = load_from_args(args)
    except (ConnectionRefusedError, FileNotFoundError, ValueError) as e:
        print(e)
        sys.exit(1)

    status = server.load(args.username, args.password, ledger.dump())

    if status == 1:
        print('Invalid username or password specified.')
        sys.exit(1)
