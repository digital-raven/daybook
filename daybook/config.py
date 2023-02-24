""" Configuration related functions.
"""

import configparser
import os
from collections import defaultdict, namedtuple
from pathlib import Path

from daybook.configs.default import create_default_ini


user_confdir = '{}/.config/daybook'.format(Path.home())
user_conf = '{}/daybook.ini'.format(user_confdir)


def get_defaults():
    """ Default values for items that should be in a config file.

    These values will be overuled by existing config entries. Useful in
    the event a config file is missing an entry.

    Returns:
        A dictionary that contains all expected entries for a
        daybook configuration file.
    """
    return {
        'primary_currency': '',
        'duplicate_window': '5',
    }


def do_first_time_setup():
    """ Create ledger root and copy default.ini to user conf path.
    """

    try:
        os.makedirs(user_confdir)
    except FileExistsError:
        pass

    # Write user-specific ini with comments.
    ini = create_default_ini()
    with open(user_conf, 'w') as f:
        f.write(ini)

    # Create ledger root
    cp = configparser.ConfigParser()
    cp.read_string(ini)


def add_config_args(args, config=None):
    """ Add params from a config file to an ArgumentParser.

    Parameters are only copied if not already set in the
    ArgumentParser.

    Args:
        args: ArgumentParser instance.
        config: Path to config file.

    Returns:
        namedtuple containing config parameters overridden by command
        line arguments.

    Raises:
        FileNotFoundError: Provided config file doesn't exist.
        KeyError: Configuration file has no default section (or no sections).
    """
    config = user_conf if not config else config

    if not os.path.exists(config):
        raise FileNotFoundError('Config {} does not exist.'.format(config))

    cp = configparser.ConfigParser()

    try:
        cp.read(config)
    except Exception as e:
        raise KeyError('Config "{}" is invalid. {}.'.format(config, e))

    if 'default' not in cp:
        raise KeyError('Config {} has no "default" section.'.format(config))

    d = get_defaults()
    d.update(cp['default'])

    # copy vals into args if not already in args.
    for key, val in d.items():
        try:
            if not getattr(args, key):
                setattr(args, key, val)
        except AttributeError:
            setattr(args, key, val)

    return args
