""" clear subcommand.
"""

import sys

from daybook.client import client


def do_clear(args):
    """ Command server to clear its ledger.
    """
    try:
        server = client.open(args.hostname, args.port)
    except ConnectionRefusedError as e:
        print(e)
        sys.exit(1)

    server.clear(args.username, args.password)
