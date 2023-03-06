""" Helper functions to dynamically import code.
"""

import importlib
import os
import sys
from pathlib import Path

from daybook.client.load import readdir_


def import_single_py(pyfile):
    """ Import a single python file as a module.

    May litter __pycache__ dirs around the place.

    Args:
        pyfile: Path to python3 code to import.

    Returns:
        module, pycache: The return from importlib.__import__ and a path
        to the __pycache__ file. Maybe your application wants to delete
        this afterwords.

    Raises:
        ModuleNotFoundError if the pyfile doesn't exist.
    """
    absdir = Path(pyfile).parent.absolute()
    basename = os.path.basename(pyfile)

    try:
        sys.path = [os.path.abspath(absdir)] + sys.path
        module = ''.join(basename.split('.py')[0:])
        module = importlib.__import__(module)
    finally:
        sys.path = sys.path[1:]

    return module, str(absdir) + os.path.sep + '__pycache__'


def import_module(pyfile, filter=lambda x: True, keys=None):
    """ Import a module

    Same as import_single_py, but enforces some conventions.

    Args:
        pyfile: Python file to import.
        filter: Filter function which accepts a module and should
            raise a KeyError, TypeError, or ValueError if the module
            was invalid.
        keys: Optional list of specific members of the module to return
            as a tuple.

    Returns:
        The imported module reference if no keys were specified, or
        a tuple of the members indicated by keys.

    Raises:
        OSError if pyfile doesn't exist.
        Whatever exception is raised by the filter function.
    """
    try:
        module, _ = import_single_py(pyfile)
    except ModuleNotFoundError:
        raise OSError(f"ERROR: {pyfile} not found.")

    # Should raise if something was wrong with the module
    filter(module)

    if keys:
        d = module.__dict__
        return (d[k] for k in keys)

    return module


def find_module(pyfile, paths, filter=lambda x: True, keys=None):
    """ Search paths for a module

    If pyfile is an exact match on its own then no paths will be searched.

    Args:
        pyfile: Exact name of pyfile to serach for.
        paths: List of dirs to search.
        filter: See import_module.
        keys: See import_module.

    Returns:
        See import_module.

    Raises:
        OSError if pyfile wasn't found in any path.
        ValueError if any path wasn't a directory.
        See import_module.
    """
    if os.path.isfile(pyfile):
        return import_module(pyfile, filter, keys)

    for path in paths:
        _, _, files = readdir_(path)
        files = [x for x in files if x.endswith('.py')]
        if pyfile in files:
            return import_module(f'{path}/{pyfile}', filter, keys)

    raise OSError(f'{pyfile} not found in any of {paths}')


def import_modules(paths, filter=lambda x: True, keys=None):
    """ Import all modules found in paths.

    If two modules have the same name then the one found earlier in the
    paths takes precedence.

    Args:
        path: List of dirs to check.
        filter: See import_module.
        keys: See import_module.

    Returns:
        A dict where the key is the basename (no .py extension) of the module
        and the values are the same as returned by import_module.

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
                    modules[basename] = import_module(f'{path}/{f}', filter, keys)
                except (KeyError, TypeError, ValueError) as e:
                    pass

    return modules
