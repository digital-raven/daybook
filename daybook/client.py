""" main entry point for daybook client program.
"""

import os
import sys
import xmlrpc.client
from collections import defaultdict

import argcomplete
import dateparser
import datetime
from prettytable import PrettyTable

import daybook.parser
from daybook.config import add_config_args, do_first_time_setup, user_conf
from daybook.Ledger import Ledger, Hints


def get_start_end(start, end, range_):
    """Compute what the start date and end date should be.

    This function is specific to daybook's argument parsing and how
    date filters should be decided when a range is provided.

    If start and range are provided, then end = start + range

    Returns:
        start, end as DateTime objects.
    """
    today = dateparser.parse('today')
    start = dateparser.parse(start) if start else None
    end = dateparser.parse(end) if end else None

    if range_:
        range_ = today - dateparser.parse(range_)

    if start and range_:
        end = start + range_
    elif end and range_:
        start = end - range_
    elif range_:
        end = today
        start = end - range_
        start.hour = 0
        start.minute = 0
        start.second = 0
        start.microsecond = 0

    return start, end


def get_dump(server, args):
    """ Get filtered dump from server.

    Only get dump involving transactions that match criterion in args.

    Args:
        args: ArgumentParser reference.

    Returns:
        Dump from server as string of CSVs.
    """
    start, end = get_start_end(args.start, args.end, args.range)
    username = args.username
    password = args.password
    accounts = ' '.join(args.accounts) if args.accounts else None
    currencies = ' '.join(args.currencies) if args.currencies else None
    types = ' '.join(args.types) if args.types else None
    tags = ':'.join(args.tags) if args.tags else None

    return server.dump(
        username, password,
        start, end,
        accounts, currencies, types, tags)


def do_clear(server, args):
    """ Command server to clear its ledger.
    """
    server.clear(args.username, args.password)


def do_dump(server, args):
    """ Retrieve transactions from daybookd as a raw csv string.
    """
    print(get_dump(server, args))


def do_expense(server, args):

    # set start date for current month
    if not args.start and not args.end and not args.range:
        args.start = datetime.date.today()
        args.start = args.start.replace(day=1)
        args.start = str(args.start)

    if not args.types:
        args.types.extend(['expense', 'income'])

    ledger = Ledger(args.primary_currency)
    ledger.load(get_dump(server, args))

    # income table
    pt = PrettyTable()
    pt.field_names = ['Account', 'Balance']
    pt.align = 'l'
    for name in sorted([x for x in ledger.accounts if ledger.accounts[x].type == 'income']):
        account = ledger.accounts[name]
        balances = []
        for cur in sorted(account.balances):
            balance = account.balances[cur]
            balances.append('{}: {}'.format(cur, -balance))

        pt.add_row([name, '\n'.join(balances)])
    print('Income')
    print(pt, '\n')

    # expense table
    pt = PrettyTable()
    pt.field_names = ['Account', 'Balance']
    pt.align = 'l'
    for name in sorted([x for x in ledger.accounts if ledger.accounts[x].type == 'expense']):
        account = ledger.accounts[name]
        balances = []
        for cur in sorted(account.balances):
            balance = account.balances[cur]
            balances.append('{}: {}'.format(cur, balance))

        pt.add_row([name, '\n'.join(balances)])
    print('Expenses')
    print(pt, '\n')

    # total cash flow
    pt = PrettyTable()
    pt.field_names = ['Currency', 'Balance']
    pt.align = 'l'

    balances = defaultdict(lambda: 0)
    for name in sorted(ledger.accounts):
        account = ledger.accounts[name]
        if (account.type in ['expense', 'income']):
            for cur in account.balances:
                balance = account.balances[cur]
                balances[cur] -= balance

    for cur, balance in balances.items():
        pt.add_row([cur, balance])

    print('Cash flow')
    print(pt, '\n')


def get_csv_paths(rootdir):
    """ Return paths to all CSVs from root.

    Args:
        rootdir: Root directory which will be recursively searched for CSVs.

    Returns:
        A list of all csv paths.
    """
    csvs = []
    for root, dirs, files in os.walk(rootdir):
        csvs.extend(['{}/{}'.format(root, f) for f in files if '.csv' in f])
    return csvs


def do_load(server, args):
    """ Load a local ledger with CSVs and dump to daybookd.
    """
    csvs = []
    hints_p = ''
    hints = None
    if args.csv:
        if args.hints:
            hints_p = args.hints

        try:
            hints = Hints(hints=hints_p)
        except Exception as e:
            print('ERROR: "{}" is not a valid hints file. {}'.format(hints_p, e))
            sys.exit(1)

        for csv in args.csv:
            if not os.path.exists(csv):
                print('ERROR: {} does not exist.'.format(csv))
                sys.exit(1)
            elif os.path.isfile(csv):
                csvs.append(csv)
            elif os.path.isdir(csv):
                csvs.extend(get_csv_paths(csv))
            else:
                print('ERROR: {} is not a regular file or dir.'.format(csv))
                sys.exit(1)

        if not csvs:
            print('ERROR: No CSVs found in specified locations.')
            return
    else:
        # find all csvs in ledger_root if no csvs provided.
        if not args.ledger_root:
            print(
                'ERROR: No ledger_root specified on '
                'command-line or in {}'.format(args.config))
            sys.exit(1)

        csvs = get_csv_paths(args.ledger_root)

        # verify hints file before verifying provided csv.
        if args.hints:
            hints_p = args.hints
        else:
            hints_p = '{}/hints'.format(args.ledger_root)
            if not os.path.exists(hints_p):
                hints_p = ''

        try:
            hints = Hints(hints=hints_p)
        except Exception as e:
            print('ERROR: "{}" is not a valid hints file. {}.'.format(hints_p, e))
            sys.exit(1)

        if not csvs:
            print('No CSVs found in {}.'.format(args.ledger_root))
            return

    ledger = Ledger(args.primary_currency, hints=hints)
    try:
        ledger.loadCsvs(csvs)
        server.load(args.username, args.password, ledger.dump())
    except ValueError as ve:
        print(ve)
        sys.exit(1)


functions = {
    'clear': do_clear,
    'dump': do_dump,
    'expense': do_expense,
    'load': do_load,
}


def main():
    parser = daybook.parser.create_main_parser()
    argcomplete.autocomplete(parser)
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
