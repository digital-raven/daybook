import os
import unittest

from daybook.client.cli.convert.main import convert_csv, convert_csvs, convert_filter
from daybook.util.importer import import_single_py, import_module


resources = f'{os.path.dirname(__file__)}/resources/convert'


def convert_row(row):
    return 'local convert_row'


class TestConvert(unittest.TestCase):
    """ Test Convert and convert CSV functions.
    """
    def test_import_single_py(self):
        """ Test importing a test python3 file.
        """
        module, _ = import_single_py(f'{resources}/test.py')
        self.assertEqual('hello there', module.hello)

        with self.assertRaises(ModuleNotFoundError):
            import_single_py(f'{resources}/not-exist.py')

    def test_import_converter(self):
        """ The same as import_single_py but check for 2 fields.
        """
        headings, convert_row = import_module(
            f'{resources}/good_convert.py',
            keys=['headings', 'convert_row'])

        self.assertEqual('headings', headings)
        self.assertEqual('some string', convert_row(None))

    def test_import_converter_doesnt_exist(self):
        """ Should raise OSError if pyfile doesn't exist.
        """
        with self.assertRaises(OSError):
            import_module(f'{resources}/doesnt_exist.py', convert_filter)

    def test_import_converter_bad_headings(self):
        """ headings needs to be a str.
        """
        with self.assertRaises(TypeError):
            import_module(f'{resources}/bad_convert_headings.py', convert_filter)

    def test_import_converter_missing_headings(self):
        """ headings should be present.
        """
        with self.assertRaises(KeyError):
            import_module(f'{resources}/bad_convert_missing_headings.py', convert_filter)

    def test_import_converter_missing_convert_row(self):
        """ convert_row should be present.
        """
        with self.assertRaises(KeyError):
            import_module(f'{resources}/bad_convert_missing_convert_row.py', convert_filter)

    def test_convert_csv(self):
        """ A CSV should be converted based on headings and convert_row.
        """
        file = f'{resources}/greetings.csv'
        rows = convert_csv(file, convert_row, 'headings')

        exp = [
            'headings',
            'local convert_row',
            'local convert_row',
        ]

        self.assertEqual(exp, rows)

    def test_convert_csv_not_found(self):
        """ Should raise OSError if file not found.
        """
        file = f'{resources}/not-exist.csv'

        with self.assertRaises(OSError):
            rows = convert_csv(file, convert_row, 'headings')

    def test_convert_csvs(self):
        """ A CSV should be converted based on headings and convert_row.
        """
        file = f'{resources}/greetings.csv'
        rows = convert_csvs([file, file], convert_row, 'headings')

        exp = [
            'headings',
            'local convert_row',
            'local convert_row',
            'local convert_row',
            'local convert_row',
        ]

        self.assertEqual(exp, rows)


if __name__ == '__main__':
    unittest.main()
