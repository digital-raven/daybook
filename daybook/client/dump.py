""" dump sucbcommand and associated functions.

A few other subcommands use get_dump
"""

import sys

import argcomplete
import dateparser

from daybook.client import client
from daybook.client.filtering import create_filter_func, format_filter_args
from daybook.client.load import local_load


def get_dump(server, args):
    """ Get filtered dump from server.

    Only get dump involving transactions that match criterion in args.

    Args:
        args: ArgumentParser reference.

    Returns:
        Dump from server as string of CSVs.
    """
    start, end, accounts, currencies, types, tags = format_filter_args(args)
    username = args.username
    password = args.password
    accounts = ' '.join(accounts)
    currencies = ' '.join(currencies)
    types = ' '.join(types)
    tags = ':'.join(tags)

    return server.dump(
        username, password,
        start, end, accounts, currencies, types, tags)


def do_dump(args):
    """ Retrieve transactions from daybookd as a raw csv string.
    """
    if not args.csvs:
        try:
            server = client.open(args.hostname, args.port)
        except ConnectionRefusedError as e:
            print(e)
            sys.exit(1)

        print(get_dump(server, args))
    else:
        ledger = local_load(args)
        filter_ = create_filter_func(args)
        print(ledger.dump(filter_))
