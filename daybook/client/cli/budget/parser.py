from daybook.client.parsergroups import csv_opts, filter_opts, server_opts


def add_subparser(subparsers):

    sp = subparsers.add_parser(
        'budget',
        help='Compare final balances of transactions against a budget.',
        description='If any CSVs are specified, then this command will '
                    'use those transactions instead of daybookd.',
        parents=[csv_opts, server_opts, filter_opts])

    sp.add_argument('-b', '--budgets', help='List of budget files.', required=True, nargs='+')
