""" clear subcommand.
"""

import sys
import xmlrpc.client


def do_clear(args):
    """ Command server to clear its ledger.
    """
    url = 'http://{}:{}'.format(args.hostname, args.port)

    try:
        server = xmlrpc.client.ServerProxy(url, allow_none=True)
        server.ping()
    except ConnectionRefusedError:
        print('ERROR: No daybookd listening at {}'.format(url))
        sys.exit(1)

    server.clear(args.username, args.password)
