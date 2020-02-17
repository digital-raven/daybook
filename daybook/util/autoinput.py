""" A function for input tab-autocompletion from a list of suggestions.
"""

import readline


class _InputCompleter:

    def __init__(self, options):
        self.options = sorted(options)

    def complete(self, text, state):
        if state == 0:  # on first trigger, build possible matches
            if text:  # cache matches (entries that start with entered text)
                self.matches = [s for s in self.options if s and s.startswith(text)]
            else:  # no text entered, all matches possible
                self.matches = self.options[:]

        # return match indexed by state
        try:
            return self.matches[state]
        except IndexError:
            return None


def autoinput(prompt='', options=None):
    """ Perform input with autocompletion.

    If no options are provided, then behaves just like regular input.

    Args:
        prompt: Prompt string for input.
        options: List of string options that can be autocompleted.

    Returns:
        The string the user input.
    """
    if not options:
        options = []

    # get old state
    orig = readline.get_completer()
    completer = _InputCompleter(options)

    # set up autocopletion
    readline.set_completer(completer.complete)
    readline.parse_and_bind('tab: complete')

    # get input
    s = input(prompt)

    # TODO: Learn how to properly reset readline.
    readline.set_completer(orig)

    return s
