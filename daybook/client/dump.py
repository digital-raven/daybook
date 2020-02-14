""" dump sucbcommand and associated functions.

A few other subcommands use get_dump
"""

import sys
import xmlrpc.client

import argcomplete
import dateparser


def _get_start_end(start, end, range_):
    """Compute what the start date and end date should be.

    This function is specific to daybook's argument parsing and how
    date filters should be decided when a range is provided.

    If start and range are provided, then end = start + range

    Returns:
        start, end as DateTime objects.
    """
    today = dateparser.parse('today')
    start = dateparser.parse(start) if start else None
    end = dateparser.parse(end) if end else None

    if range_:
        range_ = today - dateparser.parse(range_)

    if start and range_:
        end = start + range_
    elif end and range_:
        start = end - range_
    elif range_:
        end = today
        start = end - range_
        start.hour = 0
        start.minute = 0
        start.second = 0
        start.microsecond = 0

    return start, end


def get_dump(server, args):
    """ Get filtered dump from server.

    Only get dump involving transactions that match criterion in args.

    Args:
        args: ArgumentParser reference.

    Returns:
        Dump from server as string of CSVs.
    """
    start, end = _get_start_end(args.start, args.end, args.range)
    username = args.username
    password = args.password
    accounts = ' '.join(args.accounts) if args.accounts else None
    currencies = ' '.join(args.currencies) if args.currencies else None
    types = ' '.join(args.types) if args.types else None
    tags = ':'.join(args.tags) if args.tags else None

    return server.dump(
        username, password,
        start, end,
        accounts, currencies, types, tags)


def do_dump(args):
    """ Retrieve transactions from daybookd as a raw csv string.
    """
    url = 'http://{}:{}'.format(args.hostname, args.port)

    try:
        server = xmlrpc.client.ServerProxy(url, allow_none=True)
        server.ping()
    except ConnectionRefusedError:
        print('ERROR: No daybookd listening at {}'.format(url))
        sys.exit(1)

    print(get_dump(server, args))
