from daybook.client.parsergroups import create_csv_opts, create_filter_opts, create_server_opts


def add_subparser(subparsers):
    csv_opts = create_csv_opts()
    filter_opts = create_filter_opts()
    server_opts = create_server_opts()

    sp = subparsers.add_parser(
        'report',
        help='Display reports based on transactions and budgets.',
        description='If any CSVs are specified, then this command will '
                    'use those transactions instead of daybookd.',
        parents=[csv_opts, server_opts, filter_opts])

    sp.add_argument(
        '--reporter', required=True,
        help=(
            'Path to reporter module. This is a python3 script with a '
            'report(ledger, budget) function which returns a report string.'))

    sp.add_argument('-b', '--budgets', help='List of budget files.', nargs='*')
