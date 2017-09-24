# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, division
import logging
import sys


def print_error(msg):
    """
    Print a string to stderr.

    :param msg: The message to print.
    """
    print(msg, file=sys.stderr)


def decode_cli_arg(arg):
    """
    Turn a bytestring provided by `argparse` into unicode.

    :param arg: The bytestring to decode.
    :return: The argument as a unicode object.
    :raises ValueError: If arg is None.
    """
    if arg is None:
        raise ValueError('Argument cannot be None')

    if sys.version_info.major == 3:
        # already decoded
        return arg

    return arg.decode(sys.getfilesystemencoding())


def log_level_from_vebosity(verbosity):
    """
    Get the `logging` module log level from a verbosity.

    :param verbosity: The number of times the `-v` option was specified.
    :return: The corresponding log level.
    """
    if verbosity == 0:
        return logging.WARNING
    if verbosity == 1:
        return logging.INFO
    return logging.DEBUG
