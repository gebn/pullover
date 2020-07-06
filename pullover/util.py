import logging
import sys


def print_error(msg):
    """
    Print a string to stderr.

    :param str msg: The message to print.
    """
    print(msg, file=sys.stderr)


def log_level_from_vebosity(verbosity):
    """
    Get the :mod:`logging` module log level from a verbosity.

    :param int verbosity: The number of times the `-v` option was specified.
    :return: The corresponding log level.
    :rtype: int
    """
    if verbosity == 0:
        return logging.WARNING
    if verbosity == 1:
        return logging.INFO
    return logging.DEBUG
