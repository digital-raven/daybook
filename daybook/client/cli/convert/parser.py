def add_subparser(subparsers):

    sp = subparsers.add_parser(
        'convert',
        help="Convert a spreadsheet and print the results.")

    sp.add_argument(
        '--csvs', metavar='CSV',
        help='Specify CSVs or directories to load.', nargs='+', required=True)

    sp.add_argument(
        '--converter', required=True,
        help=(
            'Path to conversion module. This is a python3 script with a '
            'headings string member and a convert_row(row) function which '
            'returns a string representing the modified row.'))
