""" Hints class.
"""

import string

from daybook.util import colonconf


class Hints:
    def __init__(self, hints=''):
        """ Constructor for Hints class.

        Args:
            hints: Path to the hints file.
        """
        self.hints = {}
        if hints:
            self.load(hints)

    def load(self, hints):
        """ Load additional entries from a hints file.

        Args:
            hints: path to the hints file.

        Raises:
            FileNotFoundError or PermissionError if the file
            couldn't be opened.
        """
        d = colonconf.load(hints)

        for key, value in d.items():
            lines = [x for x in value.splitlines() if x]
            for line in lines:
                self.hints[line] = key

    def suggest(self, s):
        """ Suggest an entry given a string.

        Args:
            s: The string to search for within self.hints.

        Returns:
            If s is an exact match, then that value is returned. If not, then
            self.hints is searched for a key which contains s. If one is found,
            then that value is returned. First-come only-served.
        """
        if s in self.hints:
            return self.hints[s]

        for key, value in self.hints.items():
            if key in s:
                return value

        return ''
