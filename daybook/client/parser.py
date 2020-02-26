""" daybook client command line arguments.
"""

import argparse

from daybook.client.parsergroups import create_csv_opts, create_filter_opts, create_server_opts


def create_client_parser():
    """ Create parser for client program.

    Returns:
        Reference to the parser. Parse main command line args with
            parser.parse_args().
    """
    csv_opts = create_csv_opts()
    filter_opts = create_filter_opts()
    server_opts = create_server_opts()

    parser = argparse.ArgumentParser(
        prog='daybook',
        description=(
            'Command-line accounting. Run "daybook" with no arguments '
            'to perform first-time setup.'))

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

    # add command
    sp = subparsers.add_parser(
        'add',
        help='Add a transaction to a CSV.')

    sp.add_argument(
        'csv', help='Specify the CSV which will append the transaction.')

    sp.add_argument(
        '--hints',
        help='Specify a hints file. If not provided, then daybook will '
             'attempt to use a hints file in the same directory as the CSV.')

    group = sp.add_argument_group(
        'heading options',
        'Use these to pre-fill values as command line arguments. They will '
        'only be used if the respective headings are present in the CSV.')
    group.add_argument('--date', help='The date on which the transactino took place.')
    group.add_argument('--src', help='Name of the source account.')
    group.add_argument('--dest', help='Name of the destintion account.')
    group.add_argument('--amount', help='The amount and currencies sent and received to / from each account.')
    group.add_argument('--tags', help='Tags for the transaction. Enter like "tag1:tag2:tag3"')
    group.add_argument('--notes', help='Free-form notes on the transaction.')

    # balance command
    sp = subparsers.add_parser(
        'balance',
        help='Print balances of accounts.',
        description='If any CSVs are specified, then this command will '
                    'use those transactions instead of daybookd.',
        parents=[csv_opts, server_opts, filter_opts])

    # clear command
    sp = subparsers.add_parser(
        'clear',
        help='Clear the ledger.')

    # dump command
    sp = subparsers.add_parser(
        'dump',
        help='Dump transactions to stdout as a raw csv.',
        description='If any CSVs are specified, then this command will '
                    'use those transactions instead of daybookd.',
        parents=[csv_opts, server_opts, filter_opts])

    # expense command
    sp = subparsers.add_parser(
        'expense',
        help=(
            'Generate an expense report. The default behavior is to use '
            'the current month.'),
        description='If any CSVs are specified, then this command will '
                    'use those transactions instead of daybookd.',
        parents=[csv_opts, server_opts, filter_opts])

    # load command
    sp = subparsers.add_parser(
        'load',
        help='Load transactions from CSV(s).',
        description=(
            'No transactions will be committed if '
            'any of the CSVs contain an invalid entry.'),
        parents=[server_opts])

    sp.add_argument(
        'csvs', metavar='csv',
        help=(
            """Specify CSVs to load.

            Directories and regular CSV files may be specified. Directories
            will be recursively searched. Each directory may contain its own
            hints, which will overwrite the hints in the previous directory.

            If not provided, then daybook will use the CSVs within ledger_root.
            """),
        nargs='*')

    return parser
