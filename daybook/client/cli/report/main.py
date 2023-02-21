""" Entry point for the "report" subcommand.
"""
import os
import sys
from pathlib import Path

from prettytable import PrettyTable

from daybook.Budget import load_budgets
from daybook.client.load import load_from_args, readdir_
from daybook.util.importer import import_single_py


def find_reporter(pyfile, paths):
    """ Search paths for a reporter module

    If pyfile is an exact match on its own then no paths will be searched.

    Args:
        pyfile: Exact name of pyfile to serach for.
        paths: List of dirs to search.

    Returns:
        See import_reporter.

    Raises:
        See import_reporter.

        OSError if pyfile wasn't found in any path.

        ValueError if any path wasn't a directory.
    """
    if os.path.isfile(pyfile):
        return import_reporter(pyfile)

    for path in paths:
        _, _, files = readdir_(path)
        files = [x for x in files if '.py' in x]
        if pyfile in files:
            return import_reporter(f'{path}/{pyfile}')

    raise OSError(f'{pyfile} not found in any of {paths}')


def import_reporter(pyfile):
    """ Import the reporter module

    Same as import_single_py, but enforces some conventions.

    Args:
        pyfile: Python file to import.

    Returns:
        help, description, report, pycache

        help: Optional short description.
        description: Optional long description.
        report must be a function that accepts a ledger and budget reference.
        pycache: A path to the __pycache__ that will be created. The
            caller may wish to remove this.

    Raises:
        OSError if pyfile doesn't exist.
        KeyError if pyfile didn't have the necessary members.
    """
    try:
        report_module, pycache = import_single_py(pyfile)
    except ModuleNotFoundError:
        raise OSError(f"ERROR: {pyfile} doesn't exist.")

    d = report_module.__dict__

    try:
        report = d['report']
    except KeyError:
        raise KeyError(f'ERROR: The module {pyfile} needs to have a "report" function.')

    help = d['help'].strip() if 'help' in d else ''
    description = d['description'].strip() if 'description' in d else ''

    return help, description, report, pycache


def import_reporters(paths):
    """ Import all reporter modules found in paths.

    If two modules have the same name then the one found earlier in the
    paths takes precedence.

    Args:
        path: List of dirs to check.

    Returns:
        A dict where the key is the basename (no .py extension) of the module
        and the values are the same as returned by import_reporter..

    Raises:
        ValueError if any path wasn't a directory.
    """
    modules = {}
    for path in paths:
        _, _, files = readdir_(path)
        files = [x for x in files if '.py' in x and x not in modules]
        for f in files:
            try:
                modules[f.split('.py')[0]] = import_reporter(f'{path}/{f}')
            except KeyError:
                pass

    return modules


def list_reporters(paths):
    """ List available reporters in the path.

    Args:
        path: List of dirs to check.
    """
    pt = PrettyTable()
    pt.field_names = ['Reporter', 'Help']
    pt.align = 'l'

    modules = import_reporters(paths)

    for name, tupe in modules.items():
        help, _, _, _ = tupe
        pt.add_row([name, help])

    print(pt, '\n')


def main(args):
    """ Generate a report on transactions sent to a reporter module.
    """

    # Set up paths to search
    if 'DAYBOOK_REPORTERS' not in os.environ:
        os.environ['DAYBOOK_REPORTERS'] = f'./:{Path.home()}/.local/usr/share/daybook/presets/report'

    paths = os.environ['DAYBOOK_REPORTERS'].split(':')

    # List available reporters.
    if args.list:
        print(f'INFO: DAYBOOK_REPORTERS={os.environ["DAYBOOK_REPORTERS"]}')
        try:
            list_reporters(paths)
        except ValueError as e:
            print(e)
            sys.exit(1)
        sys.exit(0)

    if not args.reporter:
        print('ERROR: Provide a reporter via --reporter .')
        sys.exit(1)

    # Load reporter module
    reporter = args.reporter
    if not reporter.endswith('.py'):
        reporter += '.py'

    try:
        help, description, report_fun, _ = find_reporter(reporter, paths)
    except (KeyError, OSError, TypeError, ValueError) as e:
        print(e)
        sys.exit(1)

    # Print description if desired.
    if args.description:
        print(f'{args.reporter}: {help}', '\n')
        print(description)
        sys.exit(0)

    # Else load transactions and print report.
    try:
        ledger = load_from_args(args)
    except (ConnectionRefusedError, FileNotFoundError, ValueError) as e:
        print(e)
        sys.exit(1)

    try:
        budget = load_budgets(args.budgets) if args.budgets else None
    except (KeyError, FileNotFoundError) as e:
        print(e)
        sys.exit(1)

    report = report_fun(ledger, budget)
    print(report)
