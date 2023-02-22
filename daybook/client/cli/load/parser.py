from daybook.client.parsergroups import csv_opts, filter_opts, server_opts


def add_subparser(subparsers):

    sp = subparsers.add_parser(
        'load',
        help='Load transactions from CSV(s) into a daybookd.',
        description=(
            'No transactions will be committed if '
            'any of the CSVs contain an invalid entry.'),
        parents=[csv_opts, server_opts, filter_opts])
