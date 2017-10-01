# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import unittest
import datetime
import pytz
import responses
import requests
from six.moves import urllib_parse

import pullover
from pullover import Application, User
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

    SUCCESS_REQUEST = '647d2300-702c-4b38-8b2f-d56326ae460b'
    SUCCESS_JSON = {
        'status': 1,
        'request': SUCCESS_REQUEST
    }

    INVALID_USER_REQUEST = '5042853c-402d-4a18-abcb-168734a801de'
    INVALID_USER_JSON = {
        'user': 'invalid',
        'errors': ['user identifier is invalid'],
        'status': 0,
        'request': INVALID_USER_REQUEST
    }

    @staticmethod
    @responses.activate
    def _response(**kwargs):
        responses.add(responses.POST, Message._ENDPOINT, **kwargs)
        return requests.post(Message._ENDPOINT)

    def test_ok_true(self):
        self.assertTrue(
            SendResponse(self._response(json=self.SUCCESS_JSON)).ok)

    def test_ok_false(self):
        self.assertFalse(
            SendResponse(self._response(json=self.INVALID_USER_JSON)).ok)

    def test_raise_for_status_server_5xx(self):
        with self.assertRaises(ServerSendError):
            SendResponse(self._response(status=503)).raise_for_status()

    def test_raise_for_status_server_invalid_json(self):
        with self.assertRaises(ServerSendError):
            SendResponse(self._response(body='invalid_json')) \
                .raise_for_status()

    def test_raise_for_status_client(self):
        with self.assertRaises(ClientSendError):
            SendResponse(self._response(json=self.INVALID_USER_JSON)) \
                .raise_for_status()

    def test_raise_for_status_ok(self):
        SendResponse(self._response(json=self.SUCCESS_JSON)) \
            .raise_for_status()


class TestMessage(unittest.TestCase):

    _BODY = 'hello'
    _TITLE = 'title'
    _TIMESTAMP = pytz.utc.localize(datetime.datetime.utcnow()) - \
        datetime.timedelta(minutes=5)
    _EPOCH_SECONDS = int((_TIMESTAMP - Message._EPOCH_START).total_seconds())
    _URL = 'https://gebn.co.uk'
    _URL_TITLE = 'Personal Website'
    _PRIORITY = Message.HIGH
    _MESSAGE = Message(_BODY)
    _APP_TOKEN = 'foo'
    _APP = Application(_APP_TOKEN)
    _USER_KEY = 'bar'
    _USER = User(_USER_KEY)

    def test_init_url_title_no_url(self):
        with self.assertRaises(ValueError):
            Message(self._BODY, url_title=self._URL_TITLE)

    @responses.activate
    def test_send_user_agent(self):
        # ensure user agent is correctly set in request
        def callback(request):
            self.assertEqual(request.headers['User-Agent'],
                             '{0}/{1}'.format(pullover.__title__,
                                              pullover.__version__))
            return 200, {}, ''

        responses.add_callback(responses.POST, Message._ENDPOINT,
                               callback=callback)

        self._MESSAGE.send(self._APP, self._USER)

    @responses.activate
    def test_send_user_fields(self):
        def callback(request):
            params = urllib_parse.parse_qs(request.body)
            self.assertEqual(request.method, 'POST')
            self.assertEqual(params['token'][0], self._APP_TOKEN)
            self.assertEqual(params['user'][0], self._USER_KEY)
            self.assertEqual(params['message'][0], self._BODY)
            self.assertEqual(params['title'][0], self._TITLE)
            self.assertEqual(params['timestamp'][0], str(self._EPOCH_SECONDS))
            self.assertEqual(params['url'][0], self._URL)
            self.assertEqual(params['url_title'][0], self._URL_TITLE)
            self.assertEqual(params['priority'][0], str(self._PRIORITY))
            return 200, {}, ''

        responses.add_callback(responses.POST, Message._ENDPOINT,
                               callback=callback)

        Message(self._BODY, self._TITLE, self._TIMESTAMP, self._URL,
                self._URL_TITLE, self._PRIORITY).send(self._APP, self._USER)
        self.assertEqual(len(responses.calls), 1)  # no retry on response.ok

    @responses.activate
    def test_send_retry_5xx(self):
        def callback(_):
            return 503, {}, ''

        responses.add_callback(responses.POST, Message._ENDPOINT,
                               callback=callback)

        response = self._MESSAGE.send(self._APP, self._USER,
                                      retry_interval=0)  # to speed up test
        self.assertFalse(response.ok)
        self.assertEqual(len(responses.calls), Message._DEFAULT_MAX_SEND_TRIES)

    @responses.activate
    def test_send_no_retry_4xx(self):
        def callback(_):
            return 400, {}, ''

        responses.add_callback(responses.POST, Message._ENDPOINT,
                               callback=callback)

        response = self._MESSAGE.send(self._APP, self._USER)
        self.assertFalse(response.ok)
        self.assertEqual(len(responses.calls), 1)

    def test_str(self):
        self.assertEqual(str(self._MESSAGE), 'Message({0})'.format(self._BODY))
