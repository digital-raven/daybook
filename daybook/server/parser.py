""" daybookd command line arguments.
"""

import argparse


def create_server_parser():
    parser = argparse.ArgumentParser(
        prog='daybookd',
        description=(
            'Hold transactions in memory and accept queries from a '
            'daybook client.'))

    parser.add_argument('--config', help='Select custom configuration file.')
    parser.add_argument('--port', help='Listen on a custom port.')

    return parser
