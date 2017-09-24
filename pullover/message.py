# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import six
import datetime
import pytz
import backoff
import requests


class SendError(Exception):
    """
    Raised by SendResponse.raise_for_status() if a request was not successful.
    """
    pass


class ClientSendError(SendError):
    def __init__(self, status, errors):
        """
        Initialise a new error.

        :param status: The response status. Will not be 1.
        :param errors: An array of strings containing errors in the request.
        """
        super(ClientSendError, self).__init__()
        self.status = status
        self.errors = errors


class ServerSendError(SendError):
    def __init__(self, response):
        super(ServerSendError, self).__init__()
        self.response = response


class SendResponse(object):
    """
    Represents the Pushover API's response to a message send request.
    """

    @property
    def ok(self):
        """
        Find whether the response indicates the message was successfully sent.

        :return: True if it was, false otherwise.
        """
        return self._status == 1

    def __init__(self, response):
        """
        Initialise a new response.

        :param response: The requests response to parse.
        """
        self._response = response
        try:
            json = response.json()
            self._status = json['status']
            self._id = json['request']
            self._errors = json['errors'] if 'errors' in json else []
        except ValueError:
            self._status = None
            self._id = None
            self._errors = []

    def raise_for_status(self):
        """
        Raise an appropriate exception given this response.

        :raises SendError: If this response indicates a request failed.
        """
        # transport error
        if self._status is None:
            raise ServerSendError(self._response)

        # got a valid response, but may be to an invalid request
        if not self.ok:
            raise ClientSendError(self._status, self._errors)


@six.python_2_unicode_compatible
class Message(object):
    """
    Represents a Pushover message.
    """

    _ENDPOINT = 'https://api.pushover.net/1/messages.json'
    _EPOCH_START = datetime.datetime(1970, 1, 1, tzinfo=pytz.utc)
    _RETRY_INTERVAL = 5

    LOWEST = -2
    LOW = -1
    NORMAL = 0
    HIGH = 1
    # pullover does not support emergency priority messages

    def __init__(self, body, title=None, timestamp=None, url=None,
                 priority=NORMAL):
        """
        Initialise a new message.

        :param body: The contents of the message.
        :param title: The message heading. If not provided, the name of the
                      sending application will be shown.
        :param timestamp: The message datetime. Defaults to now.
        :param url: A supplementary URL to show underneath the message.
        :param priority: The message priority.
        """
        self._body = body
        self._title = title
        self._timestamp = timestamp
        self._url = url
        self._priority = priority

    def send(self, application, user):
        """
        Send this message to a user, making it originate from a given
        application. This method guarantees not to throw any exceptions.

        :param application: The application to send the message from.
        :param user: The user to send the message to. All devices will receive
                     it.
        :return: A message response object.
        """

        @backoff.on_predicate(backoff.constant,
                              lambda response: not response.ok,
                              max_tries=5,
                              interval=self._RETRY_INTERVAL)
        def send_request(sess, prepped):
            return sess.send(prepped)

        request = requests.Request(
            'POST',
            self._ENDPOINT,
            data={
                'message': self._body,
                'title': self._title,
                'timestamp': None
                if self._timestamp is None
                else int((self._timestamp - self._EPOCH_START)
                         .total_seconds()),
                'url': self._url,
                'priority': self._priority
            })
        application.sign(request)
        user.sign(request)

        with requests.session() as session:
            prepared = session.prepare_request(request)
            return SendResponse(send_request(session, prepared))

    def __str__(self):
        return '{0.__class__.__name__}({0._body})'.format(self)