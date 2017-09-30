# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division
import unittest
import sys
import logging
import six

from pullover import util


class TestPrintError(unittest.TestCase):

    _MESSAGE = 'test message'

    def test_stream(self):
        try:
            sys.stderr = six.StringIO()
            util.print_error(self._MESSAGE)
            self.assertEquals(sys.stderr.getvalue(), self._MESSAGE + '\n')
        finally:
            sys.stderr = sys.__stderr__


class TestDecodeCliArg(unittest.TestCase):

    _ARG_VALUE = 'test_arg_value'

    def test_empty(self):
        with self.assertRaises(ValueError):
            util.decode_cli_arg(None)

    @unittest.skipUnless(sys.version_info.major == 2,
                         'Only applies to Python 2')
    def test_valid_2(self):
        self.assertEqual(
            util.decode_cli_arg(
                self._ARG_VALUE.encode(sys.getfilesystemencoding())),
            self._ARG_VALUE)

    @unittest.skipUnless(sys.version_info.major == 3,
                         'Only applies to Python 3')
    def test_valid_3(self):
        self.assertEqual(util.decode_cli_arg(self._ARG_VALUE), self._ARG_VALUE)


class TestLogLevelFromVerbosity(unittest.TestCase):

    def test_warning(self):
        self.assertEqual(util.log_level_from_vebosity(0), logging.WARNING)

    def test_info(self):
        self.assertEqual(util.log_level_from_vebosity(1), logging.INFO)

    def test_debug(self):
        self.assertEqual(util.log_level_from_vebosity(2), logging.DEBUG)

    def test_default(self):
        self.assertEqual(util.log_level_from_vebosity(None), logging.DEBUG)
