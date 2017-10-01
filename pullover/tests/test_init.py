# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import unittest
import responses

import pullover
from pullover import Message
from pullover.tests import test_message


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
