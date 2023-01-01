""" Entry point for the "convert" subcommand.
"""

import csv
import sys
from collections import defaultdict

import yaml


def convert(swaps, orig):
    """ Convert a dictionary based on a swap dict.

    eg.

    orig = {key1: red, key2: blue, unused: green}
    swaps = {Favorite: key2, 2ndFavorite: key1}

    return = {Favorite: blue, 2ndFavorite: red}

    Args:
        swaps: The values in swaps correspond to the keys in d. The keys
            in swaps will hold the values in d.
        d: The dictionary to operate on and convert.

    Returns:
        A new dictionary with the swapped keys.

    Raises:
        KeyError if a key wasn't present in orig.
    """
    return {k: orig[v] for k, v in swaps.items()}


def convert_csv(swaps, file):
    """ Convert all rows of a csv.

    Args:
        swaps: See convert
        file: Path to csv.

    Returns:
        An in-order list of converted dicts.

    Raises:
        OSError if file could not be opened.
        KeyError from convert.
    """
    rows = []
    with open(file) as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(convert(swaps, row))

    return rows


def get_rules(file):
    """ Return rules as a dict

    Args:
        file: Yaml file to open.

    Returns:
        Rules as a dictionary.

    Raises:
        OSError if file could not be opened.
        ValueError if file was not in valid yaml format.
    """
    # Load rules first
    with open(file) as f:
        rules = yaml.safe_load(f.read())

    if type(rules) is not dict:
        raise ValueError(f'{file} is not in valid yaml')

    return rules


def main(args):
    """ Convert a spreadsheet's columns according to a rules file.
    """
    try:
        rules = get_rules(args.rules)
    except OSError as e:
        print(f'ERROR: Could not open {args.rules}: {e}')
        sys.exit(1)
    except ValueError as e:
        print(f'ERROR: {e}')
        sys.exit(1)

    # this gets printed
    rows = []
    for file in args.csvs:
        rows.extend(convert_csv(rules, file))

    # write to stdout
    writer = csv.DictWriter(sys.stdout, fieldnames=list(rules.keys()))

    writer.writeheader()
    writer.writerows(rows)
