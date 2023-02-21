""" main entry point for daybook client program.
"""

import importlib
import os
import sys
from pathlib import Path

import argcomplete

import daybook.client.parser
from daybook.config import add_config_args, do_first_time_setup, user_conf


def setup_reporters(args):
    """ Pre-process sys.argv to allow for pointing at custom reporters.
    """
    idx = [i for i, x in enumerate(args) if x.endswith('.py')]
    if not idx:
        return
    idx = idx[0]

    pyfile = args[idx]

    dir_ = '/'.join(pyfile.split('/')[:-1])
    if not dir_:
        dir_ = os.getcwd()

    os.environ['DAYBOOK_REPORTERS'] = dir_

    basename = pyfile.split('/')[-1]
    basename = basename.replace('.py', '').strip()

    args[idx] = basename


def setup_converters(args):
    """ Pre-process sys.argv to allow for pointing at custom converters.
    """
    idx = [i for i, x in enumerate(args) if x.endswith('.py')]
    if not idx:
        return
    idx = idx[0]

    pyfile = args[idx]

    dir_ = '/'.join(pyfile.split('/')[:-1])
    if not dir_:
        dir_ = os.getcwd()

    os.environ['DAYBOOK_CONVERTERS'] = dir_

    basename = pyfile.split('/')[-1]
    basename = basename.replace('.py', '').strip()

    args[idx] = basename


def main():

    if 'convert' in sys.argv:
        setup_converters(sys.argv)
    elif 'report' in sys.argv:
        setup_reporters(sys.argv)

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

    # set duplicate_window appropriately.
    if args.duplicate_window == 'off':
        args.duplicate_window = False
    else:
        try:
            args.duplicate_window = int(args.duplicate_window)
            if args.duplicate_window < 0:
                raise ValueError
        except ValueError:
            print('ERROR: duplicate_window must be "off" or a positive integer.')
            sys.exit(1)

    if not args.primary_currency:
        print('ERROR: No primary_currency in {}'.format(args.config))
        sys.exit(1)

    subcommand = importlib.import_module('daybook.client.cli.{}.main'.format(args.command))
    subcommand = getattr(subcommand, 'main'.format(args.command))

    try:
        subcommand(args)
    except KeyboardInterrupt:
        print('Interrupt caught - closing.')

    sys.exit(0)


if __name__ == '__main__':
    main()
