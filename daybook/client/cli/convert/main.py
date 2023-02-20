""" Entry point for the "convert" subcommand.
"""

import csv
import sys

from daybook.util.importer import import_single_py


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


def import_converter(pyfile):
    """ Import the converter module

    Same as import_single_py, but enforces some conventions.

    Args:
        pyfile: Python file to import.

    Returns:
        headings attr from pyfile. Must be a string.
        convert_row attr from pyfile. Must be a function that accepts
            a single arg as a dict.
        pycache: A path to the __pycache__ that will be created. The
            caller needs to remove this.

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

    try:
        headings = convert_module.__dict__['headings']
    except KeyError:
        raise KeyError(f'ERROR: The module {pyfile} needs to have a "headings" member.')

    if type(headings) is not str:
        raise TypeError(f'ERROR: The "headings" in {pyfile} needs to be a string')

    try:
        convert_row = convert_module.__dict__['convert_row']
    except KeyError:
        raise KeyError(f'ERROR: The module {pyfile} needs to have a "convert_row" function.')

    return headings, convert_row, pycache


def main(args):
    """ Convert a spreadsheet's columns according to a converter file.
    """
    if not args.converter.endswith('.py'):
        print(f'ERROR: {args.converter} must be a python file.')
        sys.exit(1)

    try:
        headings, convert_row, _ = import_converter(args.converter)
    except (KeyError, OSError, TypeError) as e:
        print(e)
        sys.exit(1)

    try:
        rows = convert_csvs(args.csvs, convert_row, headings)
    except OSError as e:
        print(e)
        sys.exit(1)

    print('\n'.join(rows))
