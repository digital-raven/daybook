""" Entry point for the "convert" subcommand.
"""

import csv
import os
import sys
from pathlib import Path

from daybook.util.importer import find_module

from prettytable import PrettyTable


def convert_csv(file, convert_row, headings=''):
    """ Convert rows of a csv.

    Args:
        file: Path to csv.
        convert_row: See convert_csvs.
        headings: Optional headings to add.

    Returns:
        A list of strings representing converted csv rows.

    Raises:
        OSError if file couldn't be read.

        If the convert_row function has anything wrong with it
        then that exception will be raised as well.
    """
    rows = [headings] if headings else []

    with open(file) as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(convert_row(row))

    return rows


def convert_csvs(csvs, convert_row, headings=''):
    """ Convert CSV rows according to the convert_row function

    Args:
        csvs: List of CSV files to convert.
        convert_row: A function that accepts a row of a CSV as a dict.
            Keys will be the column headings in the CSV and values are
            the values in the cells.

            This function needs to return a str.

        headings: Headings that should be printed.

    Returns:
        List of rows representing converted CSV.

    Raises:
        OSError if a csv couldn't be opened.
    """
    rows = [headings] if headings else []

    for file in csvs:
        rows.extend(convert_csv(file, convert_row))

    return rows


def convert_filter(module):
    """ Raises an KeyError of module is not a valid converter.
    """
    d = module.__dict__
    exp = ['help', 'description', 'headings', 'convert_row']
    if any([k not in d for k in exp]):
        raise KeyError(f'The module {module.__name__} needs to have {exp} members.')

    if not callable(d['convert_row']):
        raise ValueError('"convert_row" member must be a function.')


def main(args):
    """ Convert a spreadsheet's columns according to a converter file.
    """

    # Set up paths to search
    paths = ['./']
    if 'DAYBOOK_CONVERTERS' in os.environ:
        paths = os.environ['DAYBOOK_CONVERTERS'].split(':')

    # Search the path for the module if module still not found.
    converter = args.converter
    if not converter.endswith('.py'):
        converter += '.py'

    try:
        keys = ['headings', 'convert_row']
        headings, convert_row = find_module(converter, paths, convert_filter, keys)
    except (KeyError, OSError, TypeError) as e:
        print(e)
        sys.exit(1)

    if not args.csvs:
        print('ERROR: No files to convert. Specify --csvs .')
        sys.exit(1)

    try:
        rows = convert_csvs(args.csvs, convert_row, headings)
    except OSError as e:
        print(e)
        sys.exit(1)

    print('\n'.join(rows))
