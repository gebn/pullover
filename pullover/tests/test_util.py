import unittest
import sys
import logging
import io

from pullover import util


class TestPrintError(unittest.TestCase):

    _MESSAGE = 'test message'

    def test_stream(self):
        try:
            sys.stderr = io.StringIO()
            util.print_error(self._MESSAGE)
            self.assertEquals(sys.stderr.getvalue(), self._MESSAGE + '\n')
        finally:
            sys.stderr = sys.__stderr__


class TestLogLevelFromVerbosity(unittest.TestCase):

    def test_warning(self):
        self.assertEqual(util.log_level_from_vebosity(0), logging.WARNING)

    def test_info(self):
        self.assertEqual(util.log_level_from_vebosity(1), logging.INFO)

    def test_debug(self):
        self.assertEqual(util.log_level_from_vebosity(2), logging.DEBUG)

    def test_default(self):
        self.assertEqual(util.log_level_from_vebosity(None), logging.DEBUG)
