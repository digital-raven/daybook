import os
import unittest

from daybook.client.cli.report.main import import_reporter


resources = f'{os.path.dirname(__file__)}/resources/report'


class TestReport(unittest.TestCase):
    """ Test report subcommand's functions.
    """
    def test_import_reporter(self):
        """ The same as import_single_py but check fields.
        """
        report, _ = import_reporter(f'{resources}/report.py')
        self.assertEqual('some report', report(None, None))

    def test_import_reporter_doesnt_exist(self):
        """ Should raise OSError if pyfile doesn't exist.
        """
        with self.assertRaises(OSError):
            _, _ = import_reporter(f'{resources}/doesnt_exist.py')

    def test_import_reporter_missing_report(self):
        """ report function should be present.
        """
        with self.assertRaises(KeyError):
            _, _ = import_reporter(f'{resources}/bad_report_missing_report.py')


if __name__ == '__main__':
    unittest.main()
