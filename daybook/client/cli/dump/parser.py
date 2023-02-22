from daybook.client.parsergroups import create_csv_opts, create_filter_opts


def add_subparser(subparsers):
    """ Create parser for client program.

    Returns:
        Reference to the parser. Parse main command line args with
            parser.parse_args().
    """
    csv_opts = create_csv_opts()
    filter_opts = create_filter_opts()

    sp = subparsers.add_parser(
        'dump',
        help='Dump transactions to stdout as a raw csv.',
        description='If any CSVs are specified, then this command will '
                    'use those transactions instead of daybookd.',
        parents=[csv_opts, filter_opts])
