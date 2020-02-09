import os
import unittest

from daybook.Hints import Hints


resources = '{}/resources'.format(os.path.dirname(__file__))


class TestHints(unittest.TestCase):

    def test_hints(self):
        """ Verify hints can load from an ini file and find substr matches.
        """
        hints = Hints('{}/hints'.format(resources))
        self.assertEqual('', hints.suggest('micro'))
        self.assertEqual('expense.computer', hints.suggest('micro-center'))
        self.assertEqual('expense.gasoline', hints.suggest('BP BEYOND PETROLEUM #123'))
        self.assertEqual('expense.grocery', hints.suggest('WALMART Store'))
        self.assertEqual('expense.grocery', hints.suggest('TARGET #111::HI'))

    def test_load_file_not_found(self):
        """ hints.load should raise FileNotFoundError if ini does not exist.
        """
        with self.assertRaises(FileNotFoundError):
            hints = Hints('')
            hints.load('idontexist')

    def test_load_empty(self):
        """ hints should be empty if given empty file.
        """
        hints = Hints()
        hints.load('{}/empty-hints'.format(resources))
        self.assertTrue(not hints.hints)


if __name__ == '__main__':
    unittest.main()
