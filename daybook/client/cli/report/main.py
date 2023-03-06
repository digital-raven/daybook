""" Entry point for the "report" subcommand.
"""
import os
import sys
from pathlib import Path

from daybook.Budget import load_budgets
from daybook.client.load import load_from_args
from daybook.util.importer import find_module


def report_filter(module):
    """ Raises an KeyError of module is not a valid reporter.
    """
    d = module.__dict__
    exp = ['help', 'description', 'report']
    if any([k not in d for k in exp]):
        raise KeyError(f'The module {module.__name__} needs to have {exp} members.')

    if not callable(d['report']):
        raise ValueError('"report" member needs to be a function.')


def main(args):
    """ Generate a report on transactions sent to a reporter module.
    """
    paths = ['./']
    if 'DAYBOOK_REPORTERS' in os.environ:
        paths = os.environ['DAYBOOK_REPORTERS'].split(':')

    # Load reporter module
    reporter = args.reporter
    if not reporter.endswith('.py'):
        reporter += '.py'

    try:
        report_fun, = find_module(reporter, paths, report_filter, keys=['report'])
    except (KeyError, OSError, TypeError, ValueError) as e:
        print(e)
        sys.exit(1)

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
