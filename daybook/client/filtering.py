""" Convert command line args for feeding into Ledger.basic_filter.

Not elegant, but it saves a lot of copy paste for filter logic
across the subcommands, and it's all under one file.

If you're going to code a tumor, make it benign.
"""

import dateparser

from daybook.Ledger import basic_filter


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


def format_filter_args(args):
    """ Create values from args that could be passed into basic_filter.

    Useful for subcommands that allow for local computation and need
    unified logic for setting up filters from the command-line args.

    Args:
        ArgumentParser reference. Needs fields as specified in the
            'filtering' parsergroups.

    Returns:
        A 6-tuple of args that can be passed in order to basic_filter.
    """
    start, end = _get_start_end(args.start, args.end, args.range)
    accounts = set(args.accounts)
    currencies = set(args.currencies)
    types = set(args.types)
    tags = set(args.tags.replace(' ', ':').split(':')) if args.tags else set()

    return start, end, accounts, currencies, types, tags


def create_filter_func(args):
    """ Return a basic_filter function created using args.

    For use with args namespaces whose parents are the 'filtering' group.

    Args:
        args: ArgumentParser reference. Needs fields as specified in the
            'filtering' parsergroups.

    Returns:
        Lambda that can be passed to Ledger.dump().
    """
    def filter_func(x): return basic_filter(x, *format_filter_args(args))
    return filter_func
