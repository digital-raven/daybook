""" main entry point for daybook
"""

import argparse

from daybook.Ledger import Account


def create_csv_opts():
    parser = argparse.ArgumentParser(add_help=False)
    group = parser.add_argument_group(
        'csv options',
        'Options for loading CSVs from the filesystem.')
    group.add_argument(
        '--csvs', metavar='CSV',
        help='Specify CSVs or directories to load.',
        nargs='+')
    group.add_argument(
        '--duplicate-window', metavar='DAYS', default=None,
        help='Day range in which duplicate transactions will be flagged.')
    group.add_argument(
        '--hints', help='Override default loaded hints file for each CSV.')

    return parser


def create_filter_opts():
    parser = argparse.ArgumentParser(add_help=False)
    group = parser.add_argument_group(
        'filter options',
        'Only use transactions that match a filter.')
    group.add_argument(
        '--filter',
        metavar='FILTER',
        default='True',
        help='Eval transactions against a python3 conditional.'),

    return parser


csv_opts = create_csv_opts()
filter_opts = create_filter_opts()
