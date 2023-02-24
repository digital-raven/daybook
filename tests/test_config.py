import os
import unittest

from daybook.config import add_config_args, get_defaults


resources = '{}/resources/config'.format(os.path.dirname(__file__))


class MockArgs:
    """ Exists just to get attrs added on to it.
    """
    def __init__(self):
        None


class TestConfig(unittest.TestCase):
    """ For testing appropriate configuration argument resolution.
    """

    def test_empty(self):
        """ An empty config file should raise.
        """
        args = MockArgs()
        config = resources + '/empty.ini'
        with self.assertRaises(KeyError):
            add_config_args(args, config)

    def test_no_params_uses_default(self):
        """ args should be equal to get_defaults if nothing proivded.
        """
        args = MockArgs()
        config = resources + '/no-params.ini'
        add_config_args(args, config)
        self.assertEqual(get_defaults(), vars(args))

    def test_access(self):
        """ params in args should be accessible like 'args.x'.
        """
        args = MockArgs()
        config = resources + '/no-params.ini'
        add_config_args(args, config)

        self.assertEqual('', args.primary_currency)

    def test_some_params_no_args(self):
        """ config should overwrite defaults.
        """
        args = MockArgs()
        config = resources + '/some-params.ini'
        add_config_args(args, config)

        exp = get_defaults()
        exp.update({
            'primary_currency': 'config-currency',
        })

        self.assertEqual(exp, vars(args))

    def test_all_params_no_args(self):
        """ config should overwrite all defaults
        """
        args = MockArgs()
        config = resources + '/all-params.ini'
        add_config_args(args, config)

        exp = {
            'primary_currency': 'config-currency',
            'duplicate_window': '3',
        }

        self.assertEqual(exp, vars(args))

    def test_new_args(self):
        """ values exclusive to args should not be touched.
        """
        args = MockArgs()
        args.unique = 'unique'

        config = resources + '/all-params.ini'
        add_config_args(args, config)

        exp = {
            'primary_currency': 'config-currency',
            'duplicate_window': '3',
        }

        self.assertTrue(all([exp[k] == vars(args)[k] for k in exp]))
        self.assertEqual('unique', args.unique)
        self.assertEqual(len(exp) + 1, len(vars(args)))

    def test_precendence(self):
        """ values already in args should not be overwritten...
        """
        args = MockArgs()
        args.primary_currency = 'mycur'

        config = resources + '/some-params.ini'
        add_config_args(args, config)

        exp = {
            'primary_currency': 'mycur',
            'duplicate_window': '5',
        }

        self.assertEqual(exp, vars(args))

    def test_precendence2(self):
        """ ... unless those values are set but empty.
        """
        args = MockArgs()
        args.primary_currency = ''

        config = resources + '/some-params.ini'
        add_config_args(args, config)

        exp = {
            'primary_currency': 'config-currency',
            'duplicate_window': '5',
        }

        self.assertEqual(exp, vars(args))


if __name__ == '__main__':
    unittest.main()
