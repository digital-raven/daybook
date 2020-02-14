""" daybook client command line arguments.
"""

import argparse

from daybook.client.parsergroups import create_filter_opts, create_server_opts


def create_client_parser():
    """ Create parser for client program.

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
            """Specify CSVs to load.

            Directories and regular CSV files may be specified. Directories
            will be recursively searched. Each directory may contain its own
            hints, which will overwrite the hints in the previous directory.

            If not provided, then daybook will use the CSVs within ledger_root.
            """),
        nargs='*')

    return parser
