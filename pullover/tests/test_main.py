# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import unittest
import functools
import datetime
import pytz
import mock
import sys
import os
import contextlib

from pullover import __main__ as main, Message


@contextlib.contextmanager
def _suppress_stderr():
    save_stderr = sys.stderr
    try:
        sys.stderr = open(os.devnull, 'w')
        yield
    finally:
        sys.stderr.close()
        sys.stderr = save_stderr


# TODO make this default, and only require a wrapper for when these *aren't*
#      required
def _declare_app_user(f):
    @mock.patch.dict(os.environ, {'PUSHOVER_APP_ID': 'id',
                                  'PUSHOVER_USER_TOKEN': 'token'})
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

    @mock.patch.dict(os.environ, {'PUSHOVER_USER_TOKEN': 'token'})
    def test_app_explicit(self):
        self.assertEqual(main._parse_argv(self._BASE_ARGV + ['-a', 'foo']).app,
                         'foo')

    @_declare_app_user
    def test_app_implicit(self):
        self.assertEqual(main._parse_argv(self._BASE_ARGV).app, 'id')

    @mock.patch.dict(os.environ, {'PUSHOVER_USER_TOKEN': 'token'})
    def test_app_missing(self):
        with self.assertRaises(SystemExit), _suppress_stderr():
            _ = main._parse_argv(self._BASE_ARGV).app

    @mock.patch.dict(os.environ, {'PUSHOVER_APP_ID': 'id'})
    def test_user_explicit(self):
        self.assertEqual(
            main._parse_argv(self._BASE_ARGV + ['-u', 'foo']).user, 'foo')

    @_declare_app_user
    def test_user_implicit(self):
        self.assertEqual(main._parse_argv(self._BASE_ARGV).user, 'token')

    @mock.patch.dict(os.environ, {'PUSHOVER_APP_ID': 'id'})
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
    def test_message_missing(self):
        with self.assertRaises(SystemExit), _suppress_stderr():
            main._parse_argv(self._CMD)

    @_declare_app_user
    def test_message(self):
        self.assertEqual(main._parse_argv(self._BASE_ARGV).message,
                         self._MESSAGE)
