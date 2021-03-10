""" main entry point for daybook client program.
"""

import importlib
import os
import sys

import argcomplete

import daybook.client.parser
from daybook.config import add_config_args, do_first_time_setup, user_conf


def main():
    parser = daybook.client.parser.create_client_parser()
    argcomplete.autocomplete(parser)
    args = parser.parse_args()

    if not os.path.exists(user_conf) and not args.config:
        print('INFO: Running first time setup')
        do_first_time_setup()
        if not args.command:
            print('Setup complete. User config created in {}'.format(
                user_conf))
            print('Run "daybook -h" to see usage help.')
            sys.exit(0)
    elif not args.config:
        args.config = user_conf

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # fill in args with values from config.
    args = add_config_args(args, args.config)

    if not args.primary_currency:
        print('ERROR: No primary_currency in {}'.format(args.config))
        sys.exit(1)

    subcommand = importlib.import_module(
        'daybook.client.cli.{}'.format(args.command))

    subcommand = getattr(subcommand, 'do_{}'.format(args.command))

    try:
        subcommand(args)
    except KeyboardInterrupt:
        print('Interrupt caught - closing.')

    sys.exit(0)


if __name__ == '__main__':
    main()
