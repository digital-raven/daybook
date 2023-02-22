""" Entry point for the "clear" subcommand.
"""

import sys

from daybook.client import client


def main(args):
    """ Command server to clear its ledger.
    """
    try:
        server = client.open(args.hostname, args.port)
    except ConnectionRefusedError as e:
        print(e)
        sys.exit(1)

    status = server.clear(args.username, args.password)

    if status == 1:
        print('Invalid username or password specified.')
        sys.exit(1)
