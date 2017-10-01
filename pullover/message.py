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
    Derived instances of this abstract class are raised by
    :meth:`~pullover.message.SendResponse.raise_for_status()` if a request was
    not successful.
    """
    __metaclass__ = abc.ABCMeta


class ClientSendError(SendError):
    """
    Represents a message send error where we're at fault.
    """

    def __init__(self, status, errors):
        """
        Initialise a new error.

        :param int status: The response status. Will not be 1.
        :param list(str) errors: An array of strings containing errors in the
                                 request.
        """
        super(ClientSendError, self).__init__()

        #: The integer status. Will not be 1.
        self.status = status

        #: A list of textual errors
        self.errors = errors


class ServerSendError(SendError):
    """
    Represents a message send error where Pushover is experiencing issues.
    """

    def __init__(self, response):
        """
        Initialise a new error.

        :param requests.Response response: The raw requests response received.
        """
        super(ServerSendError, self).__init__()

        #: The raw requests response received
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
        :rtype: bool
        """
        return self.status == 1

    def __init__(self, response):
        """
        Initialise a new response.

        :param requests.Response response: The requests response to parse.
        """
        self._response = response
        try:
            json = response.json()

            #: The integer request status returned by Pushover. This will be
            # ``1`` in success scenarios.
            self.status = json['status']

            #: A randomly generated unique token associated with the request,
            #: e.g. ``5042853c-402d-4a18-abcb-168734a801de``.
            self.id = json['request']

            #: A list of textual errors detailing which parameters were
            #: invalid, if any.
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

    #: No notifications are generated.
    LOWEST = -2

    #: A popup, but no sound of vibration.
    LOW = -1

    #: Popup, sound and vibration. If delivered during quiet hours, this
    #: effectively becomes :attr:`~pullover.Message.LOW`.
    NORMAL = 0

    #: Same as :attr:`~pullover.Message.NORMAL`, except bypasses quiet hours,
    #: and shown in red.
    HIGH = 1

    # pullover does not support emergency priority messages

    @classmethod
    def __session(cls):
        """
        Retrieve a requests session to use within this class. Allows session
        re-use.

        :return: A new requests session if this is the first call, otherwise
                 the existing one.
        :rtype: requests.Session
        """
        if cls._session is None:
            cls._session = requests.session()
        return cls._session

    def __init__(self, body, title=None, timestamp=None, url=None,
                 url_title=None, priority=NORMAL):
        """
        Initialise a new message.

        :param str body: The contents of the message.
        :param str title: The message heading. If not provided, the name of the
                          sending application will be shown.
        :param datetime.datetime timestamp: The message datetime. Defaults to
                                            now.
        :param str url: A supplementary URL to show underneath the message.
        :param str url_title: The title for the URL above. Requires URL be set.
        :param int priority: The message priority, e.g.
                             :attr:`~pullover.Message.HIGH`. Defaults to
                             :attr:`~pullover.Message.NORMAL`.
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

    def prepare(self, application, user):
        """
        Package up this message with a sending application and user, ready for
        sending.

        :param Application application: The application to send the message
                                        from.
        :param User user: The user to send the message to. All devices will
                          receive it.
        :return: A prepared message object.
        :rtype: PreparedMessage
        """
        return PreparedMessage(self, application, user)

    def send(self, application, user, timeout=3, retry_interval=5,
             max_tries=_DEFAULT_MAX_SEND_TRIES):
        """
        Send this message to a user, making it originate from a given
        application. This method guarantees not to throw any exceptions.

        :param Application application: The application to send the message
                                        from.
        :param User user: The user to send the message to. All devices will
                          receive it.
        :param float timeout: The number of seconds to allow for each request
                              to Pushover. Defaults to 3s.
        :param float retry_interval: The amount of time to wait between
                                     requests. Defaults to 5s. Note, this is
                                     the `minimum recommended by Pushover
                                     <https://pushover.net/api#friendly>`_.
        :param int max_tries: The number of attempts to make before giving up.
                              Defaults to 5. Set this to 1 to disable back-off.
        :return: The result of the send attempt.
        :rtype: SendResponse
        """

        logger.info('Sending %s to %s using %s', self, user, application)

        def should_retry(resp):
            """
            Decides whether to retry sending a message given a response.

            :param requests.Response resp: The response to analyse.
            :return: True if the original request should be retried; false
                     otherwise.
            :rtype: bool
            """
            return not resp.ok and not (400 <= resp.status_code < 500)

        @backoff.on_predicate(backoff.constant,
                              should_retry,
                              max_tries=max_tries,
                              interval=retry_interval)
        def send_request(sess, prepped):
            """
            Sends a request to Pushover.

            :param requests.Session sess: The session to send the request with.
            :param requests.PreparedRequest prepped: The request to send.
            :return: The request response.
            :rtype: requests.Response
            """
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
        response = send_request(self.__session(), prepared)
        logger.debug('Request time: %fs', response.elapsed.total_seconds())
        return SendResponse(response)

    def __str__(self):
        return '{0.__class__.__name__}({0._body})'.format(self)


class PreparedMessage(object):
    """
    A message together with its sending application and receiving user.
    """

    def __init__(self, message, application, user):
        """
        Initialise a new prepared message.

        :param Message message: The message to send.
        :param Application application: The application to send the message
                                        from.
        :param User user: The user to send the message to. All devices will
                          receive it.
        """
        self._message = message
        self._application = application
        self._user = user

    def send(self, **kwargs):
        """
        Send this prepared message.

        :param kwargs: Additional parameters to pass to
                       :meth:`Message.send() <pullover.Message.send()>`.
        :return: The result of the send attempt.
        :rtype: SendResponse
        """
        return self._message.send(self._application, self._user, **kwargs)
