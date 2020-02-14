""" load subcommand.
"""

import os
import sys
import xmlrpc.client

from daybook.Hints import Hints
from daybook.Ledger import Ledger


def readdir_(d):
    """ Same as OS. walk executed at the first level.

    Returns:
        A 3-tuple. First entry is the root (d), second is a list of all
        directory entries within d, and the third is a list of names of
        regular files.
    """
    d = d.rstrip(os.path.sep)
    if not os.path.isdir(d):
        raise ValueError('{} is not a directory.'.format(d))

    for root, dirs, files in os.walk(d):
        return root, dirs, files


def group_csvs(root, hints=None):
    """ Return mapping from dirs to csv paths and hints files.

    If a directory is provided, then that directory is searched recursively
    for csvs. CSVs will be assigned the hints file of the previous depth
    unless another one exists at their level.

    If a regular file was provided instead, then a hints file is searched
    within that file's directory and the two are paired and returned in
    a list of len 1.

    Args:
        root: Root directory which will be recursively searched for CSVs.
        hints: The orignal caller should keep this as None.

    Returns:
        A list of dicts. The 'csvs' field contains a list of csvs
        and the 'hints' field is a corresponding Hints reference.
    """
    ret = []

    if not os.path.exists(root):
        raise FileNotFoundError('{} does not exist.'.format(root))

    if os.path.isdir(root):
        root, dirs, files = readdir_(root)
        csvs = ['{}/{}'.format(root, f) for f in files if f.endswith('.csv')]
        hints = Hints('{}/hints'.format(root)) if 'hints' in files else hints
        ret.append({'csvs': csvs, 'hints': hints})

        for d in dirs:
            ret.extend(group_csvs('{}/{}'.format(root, d), hints))

    elif os.path.isfile(root):
        pardir = os.path.dirname(root)
        if not pardir:
            pardir = '.'
        hints_p = '{}/{}'.format(pardir, 'hints')
        hints = Hints(hints_p) if os.path.isfile(hints_p) else None
        ret.append({'csvs': [root], 'hints': hints})

    else:
        raise ValueError('{} is not a regular file or directory.'.format(root))

    return ret


def do_load(args):
    """ Load a local ledger with CSVs and dump to daybookd.
    """
    url = 'http://{}:{}'.format(args.hostname, args.port)

    try:
        server = xmlrpc.client.ServerProxy(url, allow_none=True)
        server.ping()
    except ConnectionRefusedError:
        print('ERROR: No daybookd listening at {}'.format(url))
        sys.exit(1)

    levels = []
    if args.csv:
        for csv in args.csv:
            try:
                levels.extend(group_csvs(csv))
            except (FileNotFoundError, ValueError) as e:
                print(e)
                sys.exit(1)
    else:
        if not args.ledger_root:
            print(
                'ERROR: No ledger_root specified on '
                'command-line or in {}'.format(args.config))
            sys.exit(1)

        levels = group_csvs(args.ledger_root)

    if not levels:
        print('ERROR: No CSVs found in specified locations.')
        return

    ledger = Ledger(args.primary_currency)
    try:
        for level in levels:
            ledger.loadCsvs(level['csvs'], level['hints'])
        server.load(args.username, args.password, ledger.dump())
    except ValueError as ve:
        print(ve)
        sys.exit(1)
