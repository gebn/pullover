# -*- coding: utf-8 -*-
from pkg_resources import get_distribution, DistributionNotFound
import os

from pullover.exceptions import PulloverError
from pullover.application import Application
from pullover.message import Message, PreparedMessage, SendError, \
    ClientSendError, ServerSendError
from pullover.user import User


__title__ = 'pullover'
__description__ = 'The simplest Pushover API wrapper for Python.'
__author__ = 'George Brighton'
__license__ = 'MIT'
__copyright__ = 'Copyright 2017 George Brighton'


# adapted from http://stackoverflow.com/a/17638236
try:
    dist = get_distribution(__title__)
    dist_path = os.path.normcase(dist.location)
    pwd = os.path.normcase(__file__)
    if not pwd.startswith(os.path.join(dist_path, __title__)):
        raise DistributionNotFound()
    __version__ = dist.version
except DistributionNotFound:
    __version__ = 'unknown'


def send(body, user_key, app_token, **kwargs):
    """
    Send a message to a user from an application.

    :param str body: The body of the message to send.
    :param str user_key: The user key to send to.
    :param str app_token: The application token to send from.
    :param kwargs: Additional keyword arguments to pass to
                   :class:`~pullover.Message`'s initialiser.
    :return: A message send response instance.
    :rtype: SendResponse
    """
    return Message(body, **kwargs).send(Application(app_token), User(user_key))
