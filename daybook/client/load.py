""" daybook functions for loading a ledger.
"""

import os

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
        raise ValueError('"{}" is not a directory.'.format(d))

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


def load_from_local(csvs, primary_currency, duplicate_window, hints=None):
    """ Create a ledger from local csvs.

    The "CSVs" can be dirs or individual CSVs. Each will be paired with
    a hints file via group_csvs and that hints file will be passed to
    ledger.

    Args:
        csvs: List of CSVs that should be loaded.
        primary_currency: Primary currency the resulting ledger should use.
        duplicate_window: Day range in which duplicate transactions should
            be detected.  Set to False to never duplicate transactions.
        hints: If provided, then use this singular hints file for each
            CSV, rather than the hints file which otherwise have been
            paired with the CSV.

    Returns:
        A ledger loaded from local CSVs.

    Raises:
        FileNotFoundError: Any of the CSVs didn't exist.
        ValueError: Any CSV contained an invalid entry, or no CSVs
            could be found.
    """
    levels = []

    for csv in csvs:
        levels.extend(group_csvs(csv))

    if not levels:
        raise ValueError('No CSVs found in specified locations.')

    ledger = Ledger(primary_currency, duplicate_window)
    for level in levels:
        ledger.loadCsvs(level['csvs'], hints or level['hints'])

    return ledger


def load_from_args(args):
    """ Choose from where to load based on args.

    Currently just loads from CSVs but if we add a server or support for
    stdin then maybe we want to load from there.

    Args:
        args: daybook args namespace

    Returns:
        A filtered Ledger.

    Raises:
        FileNotFoundError: Any of the CSVs did not exist.
        ValueError: Any of the CSVs contained an invalid entry or args didn't
            contain enough information.
    """
    ledger = None

    hints = Hints(args.hints) if args.hints else None

    if args.csvs:
        ledger = load_from_local(
            args.csvs,
            args.primary_currency,
            args.duplicate_window,
            hints).filtered(args.filter)

    else:
        raise ValueError('No CSVs specified.')

    return ledger
