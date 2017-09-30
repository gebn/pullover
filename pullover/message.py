# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import logging
import six
import abc
import datetime
import pytz
import backoff
import requests

import pullover
from pullover.exceptions import PulloverError


logger = logging.getLogger(__name__)


class SendError(PulloverError):
    """
    Raised by SendResponse.raise_for_status() if a request was not successful.
    """
    __metaclass__ = abc.ABCMeta


class ClientSendError(SendError):
    """
    Represents a message send error where we're at fault.
    """

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
    """
    Represents a message send error where Pushover is experiencing issues.
    """

    def __init__(self, response):
        """
        Initialise a new error.

        :param response: The raw requests response received.
        """
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
        return self.status == 1

    def __init__(self, response):
        """
        Initialise a new response.

        :param response: The requests response to parse.
        """
        self._response = response
        try:
            json = response.json()
            self.status = json['status']
            self.id = json['request']
            self.errors = json['errors'] if 'errors' in json else []
        except ValueError:
            self.status = None
            self.id = None
            self.errors = []

    def raise_for_status(self):
        """
        Raise an appropriate exception given this response.

        :raises SendError: If this response indicates a request failed.
        """
        # transport error
        if self.status is None:
            raise ServerSendError(self._response)

        # got a valid response, but may be to an invalid request
        if not self.ok:
            raise ClientSendError(self.status, self.errors)


@six.python_2_unicode_compatible
class Message(object):
    """
    Represents a Pushover message.
    """

    # if more endpoints are ever supported, both of these need abstracting from
    # this class
    _ENDPOINT = 'https://api.pushover.net/1/messages.json'
    _session = None  # send() can take this as a param

    _EPOCH_START = datetime.datetime(1970, 1, 1, tzinfo=pytz.utc)

    _DEFAULT_MAX_SEND_TRIES = 5

    LOWEST = -2
    LOW = -1
    NORMAL = 0
    HIGH = 1
    # pullover does not support emergency priority messages

    @classmethod
    def __session(cls):
        """
        Retrieve a requests session to use within this class. Allows session
        re-use.

        :return: A new requests session if this is the first call, otherwise
                 the existing one.
        """
        if cls._session is None:
            cls._session = requests.session()
        return cls._session

    def __init__(self, body, title=None, timestamp=None, url=None,
                 url_title=None, priority=NORMAL):
        """
        Initialise a new message.

        :param body: The contents of the message.
        :param title: The message heading. If not provided, the name of the
                      sending application will be shown.
        :param timestamp: The message datetime. Defaults to now.
        :param url: A supplementary URL to show underneath the message.
        :param url_title: The title for the URL above. Requires URL be set.
        :param priority: The message priority.
        :raises ValueError: If a URL title is provided, but no URL.
        """
        if url_title is not None and url is None:
            raise ValueError('A URL must be provided for a URL title to be '
                             'specified')

        self._body = body
        self._title = title
        self._timestamp = timestamp
        self._url = url
        self._url_title = url_title
        self._priority = priority

    def send(self, application, user, timeout=3, retry_interval=5,
             max_tries=_DEFAULT_MAX_SEND_TRIES):
        """
        Send this message to a user, making it originate from a given
        application. This method guarantees not to throw any exceptions.

        :param application: The application to send the message from.
        :param user: The user to send the message to. All devices will receive
                     it.
        :param timeout: The number of seconds to allow for each request to
                        Pushover. Defaults to 3s.
        :param retry_interval: The amount of time to wait between requests.
                               Defaults to 5s.
        :param max_tries: The number of attempts to make before giving up.
                          Defaults to 5.
        :return: A message response object.
        """

        logger.info('Sending %s to %s using %s', self, user, application)

        def should_retry(response):
            """
            Decides whether to retry sending a message given a response.

            :param response: The response to analyse.
            :return: True if the original request should be retried; false
                     otherwise.
            """
            return not response.ok and not (400 <= response.status_code < 500)

        @backoff.on_predicate(backoff.constant,
                              should_retry,
                              max_tries=max_tries,
                              interval=retry_interval)
        def send_request(sess, prepped):
            return sess.send(prepped, timeout=timeout)

        request = requests.Request(
            'POST',
            self._ENDPOINT,
            headers={
                'User-Agent': '{0}/{1}'.format(pullover.__title__,
                                               pullover.__version__)
            },
            data={
                'message': self._body,
                'title': self._title,
                'timestamp': None
                if self._timestamp is None
                else int((self._timestamp - self._EPOCH_START)
                         .total_seconds()),
                'url': self._url,
                'url_title': self._url_title,
                'priority': self._priority
            })
        application.sign(request)
        user.sign(request)

        prepared = self.__session().prepare_request(request)
        return SendResponse(send_request(self.__session(), prepared))

    def __str__(self):
        return '{0.__class__.__name__}({0._body})'.format(self)
