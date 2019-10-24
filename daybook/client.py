""" main entry point for daybook client program.
"""

import os
import sys
import xmlrpc.client

import dateparser

import daybook.parser
from daybook.config import add_config_args, do_first_time_setup, user_conf
from daybook.Ledger import Ledger


def get_dump(server, args):
    """ Get filtered dump from server.

    Only get dump involving transactions that match criterion in args.

    Args:
        args: ArgumentParser reference.

    Returns:
        Dump from server as string of CSVs.
    """

    username = args.username
    password = args.password
    start = dateparser.parse(args.start) if args.start else None
    end = dateparser.parse(args.end) if args.end else None
    accounts = ' '.join(args.accounts) if args.accounts else None
    types = ' '.join(args.types) if args.types else None
    tags = ':'.join(args.tags) if args.tags else None

    return server.dump(username, password, start, end, accounts, types, tags)


def do_clear(server, args):
    """ Command server to clear its ledger.
    """
    server.clear(args.username, args.password)


def do_dump(server, args):
    """ Retrieve transactions from daybookd as a raw csv string.
    """
    print(get_dump(server, args))


def do_expenses(server, args):
    print('expenses')


def get_csv_paths(rootdir):
    """ Return paths to all CSVs from root.
    """
    csvs = []
    for root, dirs, files in os.walk(rootdir):
        csvs.extend(['{}/{}'.format(root, f) for f in files if '.csv' in f])
    return csvs


def do_load(server, args):
    """ Load a local ledger with CSVs and dump to daybookd.
    """
    # find all csvs in ledger_root if no csvs provided.
    csvs = args.csv if args.csv else get_csv_paths(args.ledger_root)
    hintsfile = '{}/hints.ini'.format(args.ledger_root)
    if not os.path.exists(hintsfile):
        hintsfile = ''

    if not csvs:
        print('No CSVs found in {}.'.format(args.ledger_root))
        return

    ledger = Ledger(args.primary_currency, hintsini=hintsfile)
    ledger.loadCsvs(csvs)
    server.load(args.username, args.password, ledger.dump())


def do_show(server, args):
    print('show')


def do_summary(server, args):
    print('summary')


# called during interactive mode. each function accepts args, ledger.
functions = {
    'clear': do_clear,
    'dump': do_dump,
    'expenses': do_expenses,
    'load': do_load,
    'show': do_show,
    'summary': do_summary,
}


def main():
    parser = daybook.parser.create_main_parser()
    args = parser.parse_args()

    if not os.path.exists(user_conf) and not args.config:
        print('INFO: Running first time setup')
        do_first_time_setup()
        if not args.command:
            print('Setup complete. User config created in {}'.format(
                user_conf))
            print('Run "daybook -h" to see usage help.')
            sys.exit(0)
    elif not args.config:
        args.config = user_conf

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # fill in args with values from config.
    args = add_config_args(args, args.config)

    if not args.hostname or not args.port:
        print('ERROR: No hostname or port specified.')
        sys.exit(1)

    if not args.username or not args.password:
        print('ERROR: No username or password specified.')
        sys.exit(1)

    if not args.ledger_root:
        print(
            'ERROR: No ledger_root specified on '
            'command-line or in {}'.format(args.config))
        sys.exit(1)

    if not args.primary_currency:
        print('ERROR: No primary_currency in {}'.format(args.config))
        sys.exit(1)

    url = 'http://{}:{}'.format(args.hostname, args.port)

    try:
        server = xmlrpc.client.ServerProxy(url, allow_none=True)
        server.ping()
    except ConnectionRefusedError:
        print('ERROR: No daybookd listening at {}'.format(url))
        sys.exit(1)

    functions[args.command](server, args)


if __name__ == '__main__':
    main()
