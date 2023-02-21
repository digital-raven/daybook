""" Entry point for the "convert" subcommand.
"""

import csv
import os
import sys
from pathlib import Path

from daybook.util.importer import import_single_py
from daybook.client.load import readdir_

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


def find_converter(pyfile, paths):
    """ Search paths for a converter module

    If pyfile is an exact match on its own then no paths will be searched.

    Args:
        pyfile: Exact name of pyfile to serach for.
        paths: List of dirs to search.

    Returns:
        See import_converter.

    Raises:
        See import_converter.

        OSError if pyfile wasn't found in any path.

        ValueError if any path wasn't a directory.
    """
    if os.path.isfile(pyfile):
        return import_converter(pyfile)

    for path in paths:
        _, _, files = readdir_(path)
        files = [x for x in files if x.endswith('.py')]
        if pyfile in files:
            return import_converter(f'{path}/{pyfile}')

    raise OSError(f'{pyfile} not found in any of {paths}')


def import_converter(pyfile):
    """ Import the converter module

    Same as import_single_py, but enforces some conventions.

    Args:
        pyfile: Python file to import.

    Returns:
        help, description, headings, convert_row, pycache

        help: Optional short description.
        description: Optional long description.
        headings: attr from pyfile. Must be a string.
        convert_row: Function that accepts a single arg as a dict.
        pycache: A path to the __pycache__ that will be created. The
            caller may opt to remove this.

    Raises:
        OSError if pyfile doesn't exist.
        KeyError if pyfile didn't have a headings string or
            convert_row function.
        TypeError if headings was not a str.
    """
    try:
        convert_module, pycache = import_single_py(pyfile)
    except ModuleNotFoundError:
        raise OSError(f"ERROR: {pyfile} doesn't exist.")

    d = convert_module.__dict__

    try:
        headings = d['headings']
    except KeyError:
        raise KeyError(f'ERROR: The module {pyfile} needs to have a "headings" member.')

    if type(headings) is not str:
        raise TypeError(f'ERROR: The "headings" in {pyfile} needs to be a string')

    try:
        convert_row = d['convert_row']
    except KeyError:
        raise KeyError(f'ERROR: The module {pyfile} needs to have a "convert_row" function.')

    help = d['help'].strip() if 'help' in d else ''
    description = d['description'].strip() if 'description' in d else ''

    return help, description, headings, convert_row, pycache


def import_converters(paths):
    """ Import all converter modules found in paths.

    If two modules have the same name then the one found earlier in the
    paths takes precedence.

    Args:
        path: List of dirs to check.

    Returns:
        A dict where the key is the basename (no .py extension) of the module
        and the values are the same as returned by import_converter.

    Raises:
        ValueError if any path wasn't a directory.
    """
    modules = {}
    for path in paths:
        _, _, files = readdir_(path)
        files = [x for x in files if x.endswith('.py')]
        for f in files:
            basename = f.split('.py')[0]
            if basename not in modules:
                try:
                    modules[basename] = import_converter(f'{path}/{f}')
                except KeyError:
                    pass

    return modules


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
        help, description, headings, convert_row, _ = find_converter(converter, paths)
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
