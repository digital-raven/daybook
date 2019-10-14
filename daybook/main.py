""" main entry point for daybook
"""

import os
import shlex
import sys

import daybook.parser
from daybook.Ledger import Ledger


def clear():
    if os.name == 'nt':
        _ = os.system('cls')
    else:
        _ = os.system('clear')


def show_accounts(args, ledger):
    print('accounts')
    return


def show_expenses(args, ledger):
    print('expenses')
    return


def show_summary(args, ledger):
    print('summary')
    return


def show_transactions(args, ledger):
    print('transactions')
    return


# called during interactive mode. each function accepts args, ledger.
functions = {
    'accounts': show_accounts,
    'expenses': show_expenses,
    'summary': show_summary,
    'transactions': show_transactions,
    'clear': lambda x, y: clear(),
    'quit': lambda x, y: sys.exit(0),
}


def main():
    parser = daybook.parser.create_main_parser()
    args = parser.parse_args()

    if not os.path.exists(args.root):
        print('ERROR: {} does not exist.'.format(args.root))
        return 1

    csvfiles = []
    for root, dirs, files in os.walk(args.root):
        for f in files:
            if f.endswith(".csv"):
                csvfiles.append(os.path.join(root, f))

    ledger = Ledger()
    ledger.load(csvfiles)

    parser = daybook.parser.create_interactive_parser()

    # enter interactive mode
    cmd = ''
    while True:
        try:
            line = input('Command (help for listing): ')
        except EOFError:
            print('')
            sys.exit(0)

        toks = shlex.split(line)

        if not toks or toks[0] == 'help':
            parser.print_help()
            continue
        elif toks[0] == 'cls':
            toks[0] = 'clear'

        try:
            args = parser.parse_args(toks)
        except SystemExit:
            continue

        functions[args.command](args, ledger)


if __name__ == '__main__':
    main()
