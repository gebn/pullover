# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import unittest

from pullover.message import ClientSendError


class TestClientSendError(unittest.TestCase):

    _STATUS = 1
    _ERRORS = ['foo', 'bar']

    def test_status(self):
        self.assertEqual(ClientSendError(self._STATUS, self._ERRORS).status,
                         self._STATUS)

    def test_error(self):
        self.assertEqual(ClientSendError(self._STATUS, self._ERRORS).errors,
                         self._ERRORS)
