from daybook.client.parsergroups import server_opts


def add_subparser(subparsers):

    sp = subparsers.add_parser(
        'clear',
        help="Clear the user's ledger.",
        parents=[server_opts])
