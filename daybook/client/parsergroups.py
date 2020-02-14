""" main entry point for daybook
"""

import argparse

from daybook.Ledger import Account


def create_filter_opts():
    parser = argparse.ArgumentParser(add_help=False)
    group = parser.add_argument_group(
        'filter options',
        'Use these options to only show results calculated from transactions '
        'that satisfy all specified criteria. Filter options must be '
        'specified after the command.')
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
        nargs='+')
    group.add_argument(
        '--currencies',
        help='Filter for transactions involving certain currencies.',
        metavar='CURRENCY',
        nargs='+')
    group.add_argument(
        '--types',
        help=(
            'Filter for transactions that involved an account of the '
            'matching type. Valid types are {}'.format(sorted(Account.types))),
        choices=sorted(Account.types),
        metavar='TYPE',
        default=list(),
        nargs='+')
    group.add_argument(
        '--tags',
        help=(
            'Filter for transactions that involve the matching tags. '
            'This will also include account tags.'),
        metavar='TAG',
        nargs='+')

    return parser


def create_server_opts():
    parser = argparse.ArgumentParser(add_help=False)
    group = parser.add_argument_group(
        'server options', 'Select hostname and port for daybookd.')
    group.add_argument(
        '--hostname', help='Hostname of daybookd.')
    group.add_argument(
        '--port', help='Port where daybookd is listening.')

    return parser
