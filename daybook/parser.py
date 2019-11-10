""" main entry point for daybook
"""

import argparse

from daybook.Ledger import Account


def create_filter_opts():
    filter_opts = argparse.ArgumentParser(add_help=False)
    group = filter_opts.add_argument_group(
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

    return filter_opts


def create_server_opts():
    parser = argparse.ArgumentParser(add_help=False)
    group = parser.add_argument_group(
        'server options', 'Select hostname and port for daybookd.')
    group.add_argument(
        '--hostname', help='Hostname of daybookd.')
    group.add_argument(
        '--port', help='Port where daybookd is listening.')

    return parser


def create_server_parser():
    server_opts = create_server_opts()

    parser = argparse.ArgumentParser(
        prog='daybookd',
        description=(
            'Hold transactions in memory and accept queries from a '
            'daybook client.'))

    parser.add_argument('--config', help='Select custom configuration file.')
    parser.add_argument('--port', help='Listen on a custom port.')

    return parser


def create_main_parser():
    """ Create parser for main program.

    Returns:
        Reference to the parser. Parse main command line args with
            parser.parse_args().
    """
    filter_opts = create_filter_opts()
    server_opts = create_server_opts()

    parser = argparse.ArgumentParser(
        prog='daybook',
        description=(
            'Command-line accounting. Run "daybook" with no arguments '
            'to perform first-time setup.'),
        parents=[server_opts])

    parser.add_argument(
        '--config',
        help='Select custom configuration file.')
    parser.add_argument(
        '--primary-currency',
        metavar='CURRENCY',
        help='Override primary_currency in config.')

    # begin subparsers
    subparsers = parser.add_subparsers(
        metavar='command',
        dest='command',
        description='Each has its own [-h, --help] statement.')

    # clear command
    sp = subparsers.add_parser(
        'clear',
        help='Clear the ledger.')

    # dump command
    sp = subparsers.add_parser(
        'dump',
        help='Dump transactions to stdout as a raw csv.',
        parents=[filter_opts])

    # expense command
    sp = subparsers.add_parser(
        'expense',
        help=(
            'Generate an expense report. The default behavior is to use '
            'the current month.'),
        parents=[filter_opts])

    # load command
    sp = subparsers.add_parser(
        'load',
        help='Load transactions from CSV(s).',
        description=(
            'No transactions will be committed if '
            'any of the CSVs contain an invalid entry.'))

    sp.add_argument(
        'csv',
        help=(
            """List of CSVs to load.

            Directories and regular CSV files may be specified. Directories
            will be recursively searched for CSVs.

            If not provided, then daybook will use the CSVs within ledger_root.
            """),
        nargs='*')

    sp.add_argument(
        '--ledger-root',
        metavar='DIR',
        help=(
            'Override the ledger_root in the config. The specified directory '
            'will be recursively searched for CSVs. This argument will only '
            'be used if no individual CSVs or other directories were '
            'specified. This directory may also contain a hints.ini at '
            'the top level.'))

    sp.add_argument(
        '--hints',
        metavar='HINTSFILE',
        help='Specify a custom hints.ini.')

    return parser
