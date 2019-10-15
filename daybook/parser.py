""" main entry point for daybook
"""

import argparse

from daybook.Ledger import Account


def create_main_parser():
    """ Create parser for main program.

    Returns:
        Reference to the parser. Parse main command line args with
            parser.parse_args().
    """
    parser = argparse.ArgumentParser(
        prog='daybook', description='Command-line accounting.')

    parser.add_argument(
        'root',
        help='Set root dir from which to search for CSVs.')
    parser.add_argument(
        '-c', '--command',
        help='Run the command without launching into interactive mode.')

    return parser


def create_interactive_parser():
    """ create parser used during interactive session.

    Returns:
        parser: a reference to the parent parser.
    """

    # main parser
    parser = argparse.ArgumentParser(
        prog='',
        description='Daybook interactive mode')

    group = parser.add_argument_group(
        'Filter options',
        'Use these options to only show results based on transactions '
        'that satisfy all specified criteria')
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
        help='Provide this with --start to filter within a date range. Can be'
            ' human-readable. eg. "1 month", or "2 weeks"')
    group.add_argument(
        '--accounts',
        help='Filter on transactions involving the specified account names.',
        metavar='NAME',
        nargs='+')
    group.add_argument(
        '--type',
        help='Filter for transactions that involved an account of the'
            ' matching type.',
        choices=sorted(Account.types))
    group.add_argument(
        '--tags',
        help='Filter for transactions that involve the matching tags.'
            ' This also includes account tags.',
        metavar='TAG',
        nargs='+')

    subparsers = parser.add_subparsers(
        metavar='command',
        dest='command',
        description='Each has its own [-h, --help] option.')

    # accounts command
    accounts_p = subparsers.add_parser(
        'accounts', help='Report on the specified accounts.')
    accounts_p.add_argument(
        '--transactions',
        help='Print a list of transactions grouped by account.',
        action='store_true')

    # expenses command
    expenses_p = subparsers.add_parser(
        'expenses', help='Report on expenses.')

    expenses_p.add_argument(
        '--transactions',
        help='Print a list of transactions grouped by account.',
        action='store_true')

    # summary command
    summary_p = subparsers.add_parser(
        'summary',
        help='Print a summary of assets, outstanding debt, and net-worth.')

    summary_p.add_argument(
        '--all',
        help='Include closed accounts in the report.',
        action='store_true')

    # transactions command
    transactions_p = subparsers.add_parser(
        'transactions',
        help='List transactions ordered by date.')

    # clear command
    clear_p = subparsers.add_parser(
        'clear',
        help='Clear the screen. "cls" works too.')

    # quit command
    quit_p = subparsers.add_parser(
        'quit',
        help='Exit daybook.')

    return parser
