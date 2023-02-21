def add_subparser(subparsers):

    sp = subparsers.add_parser(
        'convert',
        help="Convert a spreadsheet and print the results.")

    sp.add_argument(
        '--csvs', metavar='CSV',
        help='CSVs to convert.', nargs='+')

    sp.add_argument(
        '--list', action='store_true',
        help=(
            'List available report presets. These may be found in the paths '
            'specified by the "DAYBOOK_REPORTERS" environment variable.'))

    sp.add_argument(
        '--description', action='store_true',
        help="Print the converter's description.")

    sp.add_argument(
        '--converter',
        help=(
            'Path to conversion module. This is a python3 script with a '
            'headings string member and a convert_row(row) function which '
            'returns a string representing the modified row.'))
