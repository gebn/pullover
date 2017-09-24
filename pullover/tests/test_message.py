# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import unittest

import responses
import requests

from pullover.message import ClientSendError, ServerSendError, SendResponse, \
    Message


class TestClientSendError(unittest.TestCase):

    _STATUS = 1
    _ERRORS = ['foo', 'bar']

    def test_status(self):
        self.assertEqual(ClientSendError(self._STATUS, self._ERRORS).status,
                         self._STATUS)

    def test_error(self):
        self.assertEqual(ClientSendError(self._STATUS, self._ERRORS).errors,
                         self._ERRORS)


class TestServerSendError(unittest.TestCase):

    def test_response(self):
        response = requests.Response()
        self.assertEqual(ServerSendError(response).response, response)


class TestSendResponse(unittest.TestCase):

    _SUCCESS_JSON = {
        'status': 1,
        'request': '647d2300-702c-4b38-8b2f-d56326ae460b'
    }

    _FAIL_JSON = {
        'user': 'invalid',
        'errors': ['user identifier is invalid'],
        'status': 0,
        'request': '5042853c-402d-4a18-abcb-168734a801de'
    }

    @staticmethod
    @responses.activate
    def _response(**kwargs):
        responses.add(responses.POST, Message._ENDPOINT, **kwargs)
        return requests.post(Message._ENDPOINT)

    def test_ok_true(self):
        self.assertTrue(
            SendResponse(self._response(json=self._SUCCESS_JSON)).ok)

    def test_ok_false(self):
        self.assertFalse(
            SendResponse(self._response(json=self._FAIL_JSON)).ok)

    def test_raise_for_status_server_5xx(self):
        with self.assertRaises(ServerSendError):
            SendResponse(self._response(status=503)).raise_for_status()

    def test_raise_for_status_server_invalid_json(self):
        with self.assertRaises(ServerSendError):
            SendResponse(self._response(body='invalid_json')) \
                .raise_for_status()

    def test_raise_for_status_client(self):
        with self.assertRaises(ClientSendError):
            SendResponse(self._response(json=self._FAIL_JSON)) \
                .raise_for_status()

    def test_raise_for_status_ok(self):
        SendResponse(self._response(json=self._SUCCESS_JSON)) \
            .raise_for_status()
