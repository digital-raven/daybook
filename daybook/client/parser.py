""" daybook client command line arguments.
"""

import argparse
import sys

from daybook import __version__
from daybook.client.cli import build_out_subparsers


def print_version():
    class printVersion(argparse.Action):
        def __call__(self, parser, args, values, option_string=None):
            print(__version__)
            sys.exit(0)
    return printVersion


def create_client_parser():
    """ Create parser for client program.

    Returns:
        Reference to the parser. Parse main command line args with
            parser.parse_args().
    """
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

    parser.add_argument(
        '--version', nargs=0, help='Print the version of daybook and exit.',
        action=print_version())

    # begin subparsers
    subparsers = parser.add_subparsers(
        metavar='command',
        dest='command',
        description='Each has its own [-h, --help] statement.')

    build_out_subparsers(subparsers)

    return parser
