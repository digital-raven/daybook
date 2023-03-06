import os
from argparse import RawDescriptionHelpFormatter
from pathlib import Path

from daybook.client.parsergroups import create_csv_opts, create_filter_opts
from daybook.client.cli.report.main import report_filter
from daybook.util.importer import import_modules


presets_base = f'{Path.home()}/.local/usr/share/daybook/presets'
default_presets = f'{presets_base}/report'


def add_reporter_subparsers(subparsers, parents):

    if 'DAYBOOK_REPORTERS' not in os.environ:
        os.environ['DAYBOOK_REPORTERS'] = default_presets

    paths = os.environ['DAYBOOK_REPORTERS'].split(':')

    keys = ['help', 'description']
    reporters = import_modules(paths, report_filter, keys)
    reporters = {k: reporters[k] for k in sorted(reporters)}

    for name, tupe in reporters.items():
        help, description = tupe
        description = '\n'.join([help, '', description])
        sp = subparsers.add_parser(
            name, help=help, description=description,
            parents=parents, formatter_class=RawDescriptionHelpFormatter)

        sp.add_argument('-b', '--budgets', help='List of budget files.', nargs='*')


def add_subparser(subparsers):
    csv_opts = create_csv_opts()
    filter_opts = create_filter_opts()

    desc = f"""
    The report subcommand generates reports by calling a reporter module.
    The reporter may be one listed below, or a path to a custom reporter.
    See the manpage for instructions to write a custom reporter.

    Alternate reporter locations may be specified by the DAYBOOK_REPORTERS
    environment variable.
    """.splitlines()
    desc = '\n'.join([x.strip() for x in desc])

    sp = subparsers.add_parser(
        'report',
        help='Display reports.',
        description=desc,
        formatter_class=RawDescriptionHelpFormatter)

    reporters = sp.add_subparsers(
        metavar='reporter',
        dest='reporter',
        description='Available reporters. Each has its own [-h, --help] statement.')

    add_reporter_subparsers(reporters, [csv_opts, filter_opts])
