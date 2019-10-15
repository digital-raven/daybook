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

    return parser


def create_interactive_parser():
    """ create parser used during interactive session.

    Returns:
        parser: a reference to the parent parser.
    """

    # main parser
    parser = argparse.ArgumentParser(
        prog='',
        usage='[filters] command [args]',
        description='Daybook interactive mode. Options must be specified'
            ' before the command.')

    group = parser.add_argument_group(
        'filter options',
        'Use these options to only show results calculated from transactions '
        'that satisfy all specified criteria. Filter options must be '
        'specified before the command.')
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
        '--names',
        help='Filter for transactions involving the specified account names.',
        metavar='NAME',
        nargs='+')
    group.add_argument(
        '--types',
        help='Filter for transactions that involved an account of the'
            ' matching type. Valid types are {}'.format(sorted(Account.types)),
        choices=sorted(Account.types),
        metavar='TYPE',
        nargs='+')
    group.add_argument(
        '--tags',
        help='Filter for transactions that involve the matching tags.'
            ' This will also include account tags.',
        metavar='TAG',
        nargs='+')

    # subcommands
    subparsers = parser.add_subparsers(
        metavar='command',
        dest='command',
        description='Each has its own [-h, --help] statement.')

    # expenses command
    sp = subparsers.add_parser(
        'expenses',
        help='Generate an expense report. The default behavior is to use'
            ' the current month.')

    sp.add_argument(
        '-t', '--transactions',
        help='Print the transactions for each account.',
        action='store_true')

    # show command
    sp = subparsers.add_parser(
        'show',
        help='Print more detailed reports about accounts and transactions.')

    sp.add_argument(
        '-a', '--accounts',
        help='Print a report for each account.',
        action='store_true')
    sp.add_argument(
        '-t', '--transactions',
        help='Print a list of transactions. If --accounts is specified,'
            ' then this option will group the transactions by their accounts.',
        action='store_true')

    # summary command
    sp = subparsers.add_parser(
        'summary',
        help='Summarize assets and outstanding debt.')

    sp.add_argument(
        '--all',
        help='Include closed accounts in the report.',
        action='store_true')

    # load command
    sp = subparsers.add_parser(
        'load',
        help='Load transactions from another CSV(s).')

    sp.add_argument(
        'csv',
        help='Specify a csv to load. Daybook will exit if the csv is invalid.',
        nargs='+')

    # clear command
    sp = subparsers.add_parser(
        'clear',
        help='Clear the screen. "cls" works too.')

    # quit command
    sp = subparsers.add_parser(
        'quit',
        help='Exit daybook.')

    return parser
