""" Helper functions to dynamically import code.
"""

import importlib
import os
import sys
from pathlib import Path


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
