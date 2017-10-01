# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import unittest
import mock
import sys
import responses

import pullover
from pullover import Message
from pullover.tests import test_message


class TestInstallStatus(unittest.TestCase):

    @unittest.skipUnless(sys.version_info.major == 2,
                         'Only applies to Python 2')
    @mock.patch('os.path.normcase')
    def test_uninstalled_2(self, normcase):
        normcase.return_value = 'rubbish'
        reload(pullover)
        self.assertEqual(pullover.__version__, 'unknown')

    @unittest.skipUnless(sys.version_info.major == 3 and
                         (sys.version_info.minor == 2 or
                          sys.version_info.minor == 3),
                         'Only applies to Python 3.2 and 3.3')
    @mock.patch('os.path.normcase')
    def test_uninstalled_32_33(self, normcase):
        import imp
        normcase.return_value = 'rubbish'
        imp.reload(pullover)
        self.assertEqual(pullover.__version__, 'unknown')

    @unittest.skipUnless(sys.version_info.major == 3 and
                         sys.version_info.minor >= 4,
                         'Only applies to Python 3.4+')
    @mock.patch('os.path.normcase')
    def test_uninstalled_34_plus(self, normcase):
        import importlib
        normcase.return_value = 'rubbish'
        importlib.reload(pullover)
        self.assertEqual(pullover.__version__, 'unknown')


class TestSend(unittest.TestCase):

    @responses.activate
    def test_success(self):
        responses.add(responses.POST, Message._ENDPOINT,
                      json=test_message.TestSendResponse.SUCCESS_JSON)
        response = pullover.send('message', 'user', 'app')
        self.assertTrue(response.ok)
        self.assertEqual(response.id,
                         test_message.TestSendResponse.SUCCESS_REQUEST)

    @responses.activate
    def test_invalid_user(self):
        responses.add(responses.POST, Message._ENDPOINT,
                      json=test_message.TestSendResponse.INVALID_USER_JSON)
        response = pullover.send('message', 'user', 'app')
        self.assertFalse(response.ok)
        self.assertEqual(response.id,
                         test_message.TestSendResponse.INVALID_USER_REQUEST)
