""" load subcommand.
"""

import os
import sys

from daybook.client import client
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


def local_load(args):
    """ The 'leg work' function of load.

    Useful to other subcommands if they want to create a local ledger
    using the same logic as do_load.

    Args:
        args: Daybook args namespace. Should contain at least the same
            attrs as do_load would expect.

    Returns:
        A ledger loaded from local CSVs.

    Raises:
        FileNotFoundError: Any of the CSVs didn't exist.
        ValueError: Any of the CSVs contained an invalid entry, or no CSVs
            could be decided upon based on the args.
    """
    levels = []
    if args.csv:
        for csv in args.csv:
            levels.extend(group_csvs(csv))
    else:
        if not args.ledger_root:
            raise ValueError('No CSVs specified and no ledger_root in {}'.format(args.config))

        levels = group_csvs(args.ledger_root)

    if not levels:
        raise ValueError('No CSVs found in specified locations.')
        return

    ledger = Ledger(args.primary_currency)
    for level in levels:
        ledger.loadCsvs(level['csvs'], level['hints'])

    return ledger


def do_load(args):
    """ Load a local ledger with CSVs and dump to daybookd.
    """
    try:
        server = client.open(args.hostname, args.port)
        ledger = local_load(args)
    except (ConnectionRefusedError, FileNotFoundError, ValueError) as e:
        print(e)
        sys.exit(1)

    server.load(args.username, args.password, ledger.dump())
