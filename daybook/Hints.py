""" Hints class.
"""

import string


class Hints:
    def __init__(self, hints=''):
        """ Constructor for Hints class.

        Args:
            hints: Path to the hints file.
        """
        self.hints = {}
        if hints:
            self.load(hints)

    def _loadColonConf(self, conf):
        """ Load a colonconf as a dict.

        A colonconf is a simple conf file format where the variable names
        are allowed to contain anything, but the reason for creating this
        was to permit colons in the names.

        Some entries might look like this.

            simplevar=4
            my:var:name = line1
                line2

            multi:line2 =
                first
                second

        And the associated dict will contain the following. All keys and
        values are str type.

            {'simplevar':'4',
             'my:var:name':'line1\nline2',
             'multi:line2':'first\nsecond'}

        Values extending multiple lines require at least one preceeding
        whitespace character on the additional lines.

        Line comments are supported as well. The line must begin with a '#'
        and have no preceeding white-space.

        Args:
            conf: Path to the colon conf.

        Returns:
            A dictionary where the keys are the vars read from the file
            and the values are the associated strings.

        Raises:
            FileNotFoundError or PermissionError if the file could not
            be opened.
        """
        curvar = None
        d = {}
        s = ''

        with open(conf) as f:
            s = f.read()

        for l_ in s.splitlines():
            if l_[0:1] not in string.whitespace:
                # skip comment lines
                if '#' == l_.strip()[0:1]:
                    continue

                # else beginning of a new variable declaration.
                l_ = l_.split('=')
                curvar = l_[0].strip()
                d[curvar] = ['='.join(l_[1:]).strip()]
            else:
                # keep adding to current variable
                if curvar in d:
                    d[curvar].append(l_.strip())

        return {k: '\n'.join(v).strip() for (k, v) in d.items()}

    def load(self, hints):
        """ Load additional entries from a hints file.

        Args:
            hints: path to the hints file.

        Raises:
            FileNotFoundError or PermissionError if the file
            couldn't be opened.
        """
        d = self._loadColonConf(hints)

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
