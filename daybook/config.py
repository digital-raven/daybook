""" Configuration related functions.
"""

import configparser
import os
import random
import string
from collections import defaultdict, namedtuple
from pathlib import Path


default_conf = '/etc/daybook/default.ini'
user_confdir = '{}/.config/daybook'.format(Path.home())
user_conf = '{}/daybook.ini'.format(user_confdir)


def do_first_time_setup():
    """ Create ledger root and copy default.ini to user conf path.
    """
    charset = string.ascii_uppercase + string.digits

    # use these vals to create user config if not present in system defaults.
    default_vals = {}
    default_vals['ledger_root'] = '{}/.local/share/daybook'.format(Path.home())
    default_vals['primary_currency'] = 'dollars'
    default_vals['hostname'] = 'localhost'
    default_vals['port'] = random.randint(5000, 15000)
    default_vals['username'] = ''.join(
        random.SystemRandom().choice(charset) for _ in range(20))
    default_vals['password'] = ''.join(
        random.SystemRandom().choice(charset) for _ in range(20))

    cp = configparser.ConfigParser()

    # create empty string as conf if system default does not exist.
    if os.path.exists(default_conf):
        cp.read(default_conf)
    else:
        cp.read_string('[default]')

    # substitute hardcoded defaults for any absent values.
    for key in default_vals:
        if key not in cp['default'] or not cp['default'][key]:
            cp['default'][key] = str(default_vals[key])

    try:
        os.makedirs(user_confdir)
    except FileExistsError:
        pass

    with open(user_conf, 'w') as f:
        cp.write(f)

    try:
        os.makedirs(cp['default']['ledger_root'])
    except FileExistsError:
        pass


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
        KeyError: Configuration file has no defualt section.
    """
    config = user_conf if not config else config

    if not os.path.exists(config):
        raise FileNotFoundError('Config {} does not exist.'.format(config))

    cp = configparser.ConfigParser()
    cp.read(config)

    if 'default' not in cp:
        raise KeyError('Config {} has no "default" section.'.format(config))

    # copy vals from config file into args if not already in args.
    for key in cp['default']:
        try:
            if not getattr(args, key):
                setattr(args, key, cp['default'][key])
        except AttributeError:
                setattr(args, key, cp['default'][key])

    return args
