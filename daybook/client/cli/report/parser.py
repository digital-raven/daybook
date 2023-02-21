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
        '--list', action='store_true',
        help=(
            'List available report presets. These may be found in the paths '
            'specified by the "DAYBOOK_REPORTERS" environment variable.'))

    sp.add_argument(
        '--description', action='store_true',
        help="Print the reporter's description.")

    sp.add_argument('-b', '--budgets', help='List of budget files.', nargs='*')

    sp.add_argument(
        '--reporter',
        help=(
            'Select a reporter module. This is a python3 script with a '
            'report(ledger, budget) function which returns a string.'))
