from daybook.client.parsergroups import csv_opts, filter_opts, server_opts


def add_subparser(subparsers):

    sp = subparsers.add_parser(
        'balance',
        help='Print balances of accounts.',
        description='If any CSVs are specified, then this command will '
                    'use those transactions instead of daybookd.',
        parents=[csv_opts, server_opts, filter_opts])
