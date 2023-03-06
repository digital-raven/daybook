import os
import unittest

from daybook.client.cli.report.main import report_filter
from daybook.util.importer import import_module


resources = f'{os.path.dirname(__file__)}/resources/report'


class TestReport(unittest.TestCase):
    """ Test report subcommand's functions.
    """
    def test_import_reporter(self):
        """ Valid report import.
        """
        report, = import_module(f'{resources}/report.py', report_filter, keys=['report'])
        self.assertEqual('some report', report(None, None))

    def test_import_reporter_doesnt_exist(self):
        """ Should raise OSError if pyfile doesn't exist.
        """
        with self.assertRaises(OSError):
            import_module(f'{resources}/doesnt_exist.py', report_filter)

    def test_import_reporter_missing_report(self):
        """ report function should be present.
        """
        with self.assertRaises(KeyError):
            import_module(f'{resources}/bad_report_missing_report.py', report_filter)


if __name__ == '__main__':
    unittest.main()
