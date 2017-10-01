# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import six


@six.python_2_unicode_compatible
class User(object):
    """
    Encapsulates a Pushover user key, and signs requests with it.
    """

    def __init__(self, key):
        """
        Initialise a new user.

        :param str key: The user key.
        """
        self._key = key

    def sign(self, request):
        """
        Modify a request to indicate that a new message was sent by this user.

        :param requests.Request request: The request to sign.
        """
        request.data['user'] = self._key

    def __str__(self):
        return '{0.__class__.__name__}({0._key})'.format(self)
