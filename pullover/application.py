# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import six


@six.python_2_unicode_compatible
class Application(object):
    """
    A Pushover application.
    """

    def __init__(self, token):
        """
        Initialise a new application.

        :param token: The application token.
        """
        self._token = token

    def sign(self, request):
        """
        Modify a request to indicate that a new message was sent by this
        application.

        :param request: The request to sign.
        """
        request.data['token'] = self._token

    def __str__(self):
        return '{0.__class__.__name__}({0._token})'.format(self)
