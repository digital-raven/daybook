import os
import unittest

from daybook.client.cli.convert.main import convert, convert_csv, get_rules


resources = f'{os.path.dirname(__file__)}/resources/convert'


class TestConvert(unittest.TestCase):
    """ Test Convert and convert CSV functions.
    """
    def test_convert(self):
        """ Simple swap test.

        Order shoul also depend on swaps
        """
        orig = {
            'k1': 'v1',
            'k2': 'v2',
        }

        swaps = {
            'key2': 'k2',
            'key1': 'k1',
        }

        exp = {
            'key2': 'v2',
            'key1': 'v1',
        }

        act = convert(swaps, orig)
        self.assertEqual(exp, act)

        self.assertEqual(['key2', 'key1'], list(act.keys()))

    def test_get_rules(self):
        """ Verify rules file can be read from valid yaml.
        """
        exp = {
            'Greeting': 'greeting',
            'Response': 'response',
        }
        act = get_rules(f'{resources}/rules.yaml')

        self.assertEqual(exp, act)

    def test_get_rules_bad_yaml(self):
        """ get_rules should raise ValueError on bad yaml
        """
        with self.assertRaises(ValueError):
            get_rules(f'{resources}/bad-rules.yaml')

    def test_get_rules_file_not_found(self):
        """ Verify rules file can be read from valid yaml.
        """
        with self.assertRaises(OSError):
            get_rules(f'{resources}/doesnt-exist.yaml')

    def test_convert_csv(self):
        """ Verify rules file can be read from valid yaml.
        """
        rules = get_rules(f'{resources}/rules.yaml')
        act = convert_csv(rules, f'{resources}/greetings.csv')
        exp = [
                {'Greeting': 'hello', 'Response': 'goodbye'},
                {'Greeting': 'hola', 'Response': 'adios'},
        ]

        self.assertEqual(exp, act)


if __name__ == '__main__':
    unittest.main()
