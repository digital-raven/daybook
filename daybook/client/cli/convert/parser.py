import os
from argparse import RawDescriptionHelpFormatter
from pathlib import Path

from daybook.client.cli.convert.main import import_converters


presets_base = f'{Path.home()}/.local/usr/share/daybook/presets'
default_presets = f'{presets_base}/convert'


def add_converter_subparsers(subparsers):

    if 'DAYBOOK_CONVERTERS' not in os.environ:
        os.environ['DAYBOOK_CONVERTERS'] = default_presets

    paths = os.environ['DAYBOOK_CONVERTERS'].split(':')

    converters = import_converters(paths)
    converters = {k: converters[k] for k in sorted(converters)}

    for name, tupe in converters.items():
        help, description, _, _, _ = tupe
        description = '\n'.join([help, '', description])
        sp = subparsers.add_parser(
            name, help=help, description=description,
            formatter_class=RawDescriptionHelpFormatter)

        sp.add_argument(
            '--csvs', metavar='CSV',
            help='CSVs to convert.', nargs='+')


def add_subparser(subparsers):

    desc = f"""
    The convert subcommand converts CSVs to daybook's format by calling a
    converter module. The converter may be one listed below, or a path to a
    custom one. See the manpage for instructions to write a custom conversion
    module.

    Alternate converter locations may be specified by the DAYBOOK_CONVERTERS
    environment variable.
    """.splitlines()

    desc = '\n'.join([x.strip() for x in desc])

    sp = subparsers.add_parser(
        'convert',
        help="Convert a spreadsheet and print the results.",
        description=desc,
        formatter_class=RawDescriptionHelpFormatter)

    converters = sp.add_subparsers(
        metavar='converter',
        dest='converter',
        description='Available converters. Each has its own [-h, --help] statement.')

    add_converter_subparsers(converters)
