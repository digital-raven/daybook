""" Function to parse a "colonconf".

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
"""

import string


def load(conf):
    """ Load a colonconf as a dict.

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
