def add_subparser(subparsers):

    sp = subparsers.add_parser(
        'add',
        help='Add a transaction to a CSV.')

    sp.add_argument(
        'csv', help='Specify the CSV which will append the transaction.')

    sp.add_argument(
        '--hints',
        help='Specify a hints file. If not provided, then daybook will '
             'attempt to use a hints file in the same directory as the CSV.')

    group = sp.add_argument_group(
        'heading options',
        'Use these to pre-fill values as command line arguments. They will '
        'only be used if the respective headings are present in the CSV.')
    group.add_argument('--date', help='The date on which the transactino took place.')
    group.add_argument('--src', help='Name of the source account.')
    group.add_argument('--dest', help='Name of the destintion account.')
    group.add_argument('--amount', help='The amount and currencies sent and received to / from each account.')
    group.add_argument('--tags', help='Tags for the transaction. Enter like "tag1:tag2:tag3"')
    group.add_argument('--notes', help='Free-form notes on the transaction.')
