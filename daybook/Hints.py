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

        for k, v in d.items():
            lines = [x.strip() for x in v.splitlines() if x.strip()]
            if k not in self.hints:
                self.hints[k] = lines
            else:
                self.hints[k].extend(lines)

    def suggest(self, s):
        """ Suggest an entry given a string.

        Args:
            s: The string to search for within self.hints.

        Returns:
            The key in hints for which a value was a substring of s.
        """
        for k, v in self.hints.items():
            if any([line in s for line in v]):
                return k

        return ''
