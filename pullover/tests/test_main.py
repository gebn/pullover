import argparse
import unittest
from unittest import mock
import functools
import datetime
import pytz
import sys
import os
import io
import contextlib
import responses

from pullover import __main__ as main, Message
from pullover.__main__ import EnvDefault, DependencyAction, PriorityAction
from pullover.tests import test_message


@contextlib.contextmanager
def _suppress_stderr():
    save_stderr = sys.stderr
    try:
        sys.stderr = open(os.devnull, 'w')
        yield
    finally:
        sys.stderr.close()
        sys.stderr = save_stderr


class TestEnvDefault(unittest.TestCase):

    # N.B. environment is sampled in add_argument() - cannot call this outside
    #      of test

    def test_no_env(self):
        with self.assertRaises(ValueError):
            EnvDefault(None)

    def test_no_env_defined(self):
        with self.assertRaises(SystemExit), _suppress_stderr():
            parser = argparse.ArgumentParser()
            parser.add_argument('-a', action=EnvDefault, env='SOMETHING')
            parser.parse_args([])

    @mock.patch.dict(os.environ, {'SOMETHING': 'envvalue'})
    def test_env_defined(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('-a', action=EnvDefault, env='SOMETHING')
        namespace = parser.parse_args([])
        self.assertEqual(namespace.a, 'envvalue')

    @mock.patch.dict(os.environ, {'SOMETHING': 'envvalue'})
    def test_precedence(self):
        # explicit value (foo) should always take precedence over implicit
        # value (envvalue)
        parser = argparse.ArgumentParser()
        parser.add_argument('-a', action=EnvDefault, env='SOMETHING')
        namespace = parser.parse_args(['-a', 'foo'])
        self.assertEqual(namespace.a, 'foo')


class TestDependencyAction(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        parser = argparse.ArgumentParser()
        parser.add_argument('-a')
        parser.add_argument('-b', action=DependencyAction, depends_on='a')
        cls.parser = parser

    def test_no_depends_on(self):
        with self.assertRaises(ValueError):
            DependencyAction('', '', None)

    def test_depencency_violated(self):
        with self.assertRaises(SystemExit), _suppress_stderr():
            self.parser.parse_args(['-b', 'foo'])  # missing a

    def test_dependency_satisfied(self):
        namespace = self.parser.parse_args(['-a', 'foo', '-b', 'bar'])
        self.assertEqual(namespace.b, 'bar')


class TestPriorityAction(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        parser = argparse.ArgumentParser()
        parser.add_argument('-p',
                            action=PriorityAction,
                            default=Message.NORMAL)
        cls.parser = parser

    def test_invalid_value(self):
        with self.assertRaises(SystemExit), _suppress_stderr():
            self.parser.parse_args(['-p', 'invalid'])

    def test_integral(self):
        self.assertEqual(self.parser.parse_args(['-p', '-1']).p, -1)

    def test_string(self):
        self.assertEqual(self.parser.parse_args(['-p', 'high']).p,
                         Message.HIGH)


# TODO make this default, and only require a wrapper for when these *aren't*
#      required
def _declare_app_user(f):
    @mock.patch.dict(os.environ, {'PUSHOVER_APP_TOKEN': 'token',
                                  'PUSHOVER_USER_KEY': 'key'})
    @functools.wraps(f)
    def wrapper(self):
        f(self)

    return wrapper


class TestParseArgs(unittest.TestCase):

    _CMD = ['pullover']
    _MESSAGE = 'hello'
    _BASE_ARGV = _CMD + [_MESSAGE]

    @_declare_app_user
    def test_version(self):
        with self.assertRaises(SystemExit), _suppress_stderr():
            main._parse_argv(['-V'])

    @_declare_app_user
    def test_verbosity_implicit(self):
        self.assertEqual(main._parse_argv(self._BASE_ARGV).verbosity, 0)

    @_declare_app_user
    def test_verbosity_count(self):
        self.assertEqual(main._parse_argv(self._BASE_ARGV +
                                          ['-vvvv']).verbosity,
                         4)

    @mock.patch.dict(os.environ, {'PUSHOVER_USER_KEY': 'key'})
    def test_app_explicit(self):
        self.assertEqual(main._parse_argv(self._BASE_ARGV + ['-a', 'foo']).app,
                         'foo')

    @_declare_app_user
    def test_app_implicit(self):
        self.assertEqual(main._parse_argv(self._BASE_ARGV).app, 'token')

    @mock.patch.dict(os.environ, {'PUSHOVER_USER_KEY': 'key'})
    def test_app_missing(self):
        with self.assertRaises(SystemExit), _suppress_stderr():
            _ = main._parse_argv(self._BASE_ARGV).app

    @mock.patch.dict(os.environ, {'PUSHOVER_APP_TOKEN': 'token'})
    def test_user_explicit(self):
        self.assertEqual(
            main._parse_argv(self._BASE_ARGV + ['-u', 'foo']).user, 'foo')

    @_declare_app_user
    def test_user_implicit(self):
        self.assertEqual(main._parse_argv(self._BASE_ARGV).user, 'key')

    @mock.patch.dict(os.environ, {'PUSHOVER_APP_TOKEN': 'token'})
    def test_user_missing(self):
        with self.assertRaises(SystemExit), _suppress_stderr():
            _ = main._parse_argv(self._BASE_ARGV).user

    @_declare_app_user
    def test_priority_default(self):
        self.assertEqual(main._parse_argv(self._BASE_ARGV).priority,
                         Message.NORMAL)

    @_declare_app_user
    def test_priority_explicit(self):
        self.assertEqual(
            main._parse_argv(self._BASE_ARGV + ['-p', '1']).priority,
            Message.HIGH)

    @_declare_app_user
    def test_priority_invalid(self):
        with self.assertRaises(SystemExit), _suppress_stderr():
            _ = main._parse_argv(self._BASE_ARGV + ['-p', '99'])

    @_declare_app_user
    def test_title(self):
        self.assertEqual(
            main._parse_argv(self._BASE_ARGV + ['-t', 'title']).title, 'title')

    @_declare_app_user
    def test_timestamp(self):
        dt = pytz.utc.localize(datetime.datetime.utcnow())
        self.assertEqual(
            main._parse_argv(self._BASE_ARGV +
                             ['--timestamp', dt.isoformat()]).timestamp,
            dt)

    @_declare_app_user
    def test_url(self):
        url = 'https://gebn.co.uk'
        self.assertEqual(
            main._parse_argv(self._BASE_ARGV + ['--url', url]).url, url)

    @_declare_app_user
    def test_url_title_no_url(self):
        with self.assertRaises(SystemExit), _suppress_stderr():
            main._parse_argv(self._BASE_ARGV + ['--url-title', 'foo'])

    @_declare_app_user
    def test_url_title(self):
        url = 'https://gebn.co.uk'
        url_title = 'Personal Website'
        self.assertEqual(
            main._parse_argv(self._BASE_ARGV + ['--url', url, '--url-title',
                                                url_title]).url_title,
            url_title)

    @_declare_app_user
    def test_message_missing(self):
        with self.assertRaises(SystemExit), _suppress_stderr():
            main._parse_argv(self._CMD)

    @_declare_app_user
    def test_message(self):
        self.assertEqual(main._parse_argv(self._BASE_ARGV).message,
                         self._MESSAGE)


class TestMain(unittest.TestCase):

    _INVALID_APP_JSON = {
        'token': 'invalid',
        'errors': [
            'application token is invalid'
        ],
        'status': 0,
        'request': '6f2e75b0-8ad8-4c80-9e0f-3386947f727e'
    }

    def test_argparse_failure(self):
        with self.assertRaises(SystemExit), _suppress_stderr():
            main.main(['pullover'])

    @mock.patch('sys.stderr', new_callable=io.StringIO)
    @responses.activate
    def test_invalid_app(self, mock_stderr):
        responses.add(responses.POST, Message._ENDPOINT,
                      json=self._INVALID_APP_JSON)
        status_code = main.main(['pullover', '-a', 'invalid', '-u', 'valid',
                                 'baz'])
        self.assertEqual(mock_stderr.getvalue(),
                         'application token is invalid' + os.linesep)
        self.assertEqual(status_code, 1)

    @mock.patch('sys.stdout', new_callable=io.StringIO)
    @responses.activate
    def test_valid(self, mock_stdout):
        responses.add(responses.POST, Message._ENDPOINT,
                      json=test_message.TestSendResponse.SUCCESS_JSON)
        status_code = main.main(['pullover', '-a', 'valid', '-u', 'valid',
                                 'baz'])
        self.assertEqual(
            mock_stdout.getvalue(),
            test_message.TestSendResponse.SUCCESS_REQUEST + os.linesep)
        self.assertEqual(status_code, 0)


class TestMainCli(unittest.TestCase):

    @mock.patch.object(main, 'main')
    def test_success(self, mocked):
        mocked.return_value = 0
        self.assertEqual(main.main_cli(), 0)
