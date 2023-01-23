from daybook.client.parsergroups import csv_opts, filter_opts, server_opts


def add_subparser(subparsers):

    sp = subparsers.add_parser(
        'expense',
        help=(
            'Generate an expense report. The default behavior is to use '
            'the current month.'),
        description='If any CSVs are specified, then this command will '
                    'use those transactions instead of daybookd.',
        parents=[csv_opts, server_opts, filter_opts])
