def add_subparser(subparsers):

    sp = subparsers.add_parser(
        'convert',
        help="Convert a spreadsheet and print the results.")

    sp.add_argument(
        '--csvs', metavar='CSV',
        help='Specify CSVs or directories to load.', nargs='+', required=True)

    sp.add_argument('--rules', help='Path to rules file.', required=True)
