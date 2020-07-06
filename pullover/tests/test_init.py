import unittest
from unittest import mock
import sys
import responses

import pullover
from pullover import Message
from pullover.tests import test_message


class TestInstallStatus(unittest.TestCase):

    @mock.patch('os.path.normcase')
    def test_uninstalled(self, normcase):
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
