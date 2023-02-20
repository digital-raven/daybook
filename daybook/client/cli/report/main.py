""" Entry point for the "report" subcommand.
"""

import sys

from daybook.util.importer import import_single_py


def import_reporter(pyfile):
    """ Import the reporter module

    Same as import_single_py, but enforces some conventions.

    Args:
        pyfile: Python file to import.

    Returns:
        report attr from pyfile. Must be a function that accepts
            a ledger and budget reference.
        pycache: A path to the __pycache__ that will be created. The
            caller needs to remove this.

    Raises:
        OSError if pyfile doesn't exist.
        KeyError if pyfile didn't have the necessary members.
    """
    try:
        report_module, pycache = import_single_py(pyfile)
    except ModuleNotFoundError:
        raise OSError(f"ERROR: {pyfile} doesn't exist.")

    try:
        report = report_module.__dict__['report']
    except KeyError:
        raise KeyError(f'ERROR: The module {pyfile} needs to have a "report" function.')

    return report, pycache


def main(args):
    """ Generate a report based on transactions and a budget sent to a reporter module.
    """
    if not args.reporter.endswith('.py'):
        print(f'ERROR: {args.reporter} must be a python file.')
        sys.exit(1)

    try:
        report_fun, _ = import_reporter(args.reporter)
    except (KeyError, OSError, TypeError) as e:
        print(e)
        sys.exit(1)

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
