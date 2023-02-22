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
        'Only use transactions that satisfy the specified criteria.')
    group.add_argument(
        '--start',
        metavar='DATE',
        help='Filter for transactions after this date.')
    group.add_argument(
        '--end',
        metavar='DATE',
        help='Filter for transactions before this date.')
    group.add_argument(
        '--range',
        help=(
            'Provide this with --start to filter within a date range. Can be '
            'human-readable. eg. "1 month", or "2 weeks"'))
    group.add_argument(
        '--accounts',
        help='Filter for transactions involving the specified account names.',
        metavar='NAME',
        nargs='+', default=[])
    group.add_argument(
        '--currencies',
        help='Filter for transactions involving certain currencies.',
        metavar='CURRENCY',
        nargs='+', default=[])
    group.add_argument(
        '--types',
        help=(
            'Filter for transactions that involved an account of the '
            'matching type. Valid types are {}'.format(sorted(Account.types))),
        choices=sorted(Account.types),
        metavar='TYPE',
        default=[],
        nargs='+')
    group.add_argument(
        '--tags',
        help='Filter for transactions that involve any of the tags specified.'
             'here. Tags should be provided as a single '
             'colon-separated string.',
        metavar='TAGS', default='')

    return parser


csv_opts = create_csv_opts()
filter_opts = create_filter_opts()
