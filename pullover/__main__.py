#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
import logging
import sys
import os
import argparse
import dateutil.parser

import pullover
from pullover import util, Message, User, Application


logger = logging.getLogger(__name__)


class EnvDefault(argparse.Action):
    """
    Uses an environment variable as the default value for an argument. If the
    specified environment variable is not set, the argument becomes required.
    Adapted from https://stackoverflow.com/a/10551190.
    """

    def __init__(self, env, required=True, default=None, **kwargs):
        if env is None:
            raise ValueError('env must be provided')
        if env in os.environ:
            default = os.environ[env]
            required = False
        super(EnvDefault, self).__init__(default=default, required=required,
                                         **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, values)


def _parse_argv(argv):
    """
    Interpret command line arguments.

    :param argv: `sys.argv`
    :return: The populated argparse namespace.
    """

    parser = argparse.ArgumentParser(prog=pullover.__title__,
                                     description=pullover.__description__)
    parser.add_argument('-V', '--version',
                        action='version',
                        version='%(prog)s ' + pullover.__version__)
    parser.add_argument('-v', '--verbosity',
                        help='increase output verbosity',
                        action='count',
                        default=0)
    parser.add_argument('-a', '--app',
                        action=EnvDefault,
                        env='PUSHOVER_APP_ID',
                        type=util.decode_cli_arg,
                        help='the application ID to send from; defaults to '
                             'PUSHOVER_APP_ID')
    parser.add_argument('-u', '--user',
                        action=EnvDefault,
                        env='PUSHOVER_USER_TOKEN',
                        type=util.decode_cli_arg,
                        help='the user token to send to; defaults to '
                             'PUSHOVER_USER_TOKEN')
    parser.add_argument('-p', '--priority',
                        type=int,
                        help='the integer priority of the message',
                        default=0)
    parser.add_argument('-t', '--title',
                        type=util.decode_cli_arg,
                        help='the title of the message; defaults to the name '
                             'of the sending application')
    parser.add_argument('--timestamp',
                        type=dateutil.parser.parse,
                        help='the timestamp of the message, in ISO 8601 '
                             'format; defaults to now')
    parser.add_argument('--url',
                        type=util.decode_cli_arg,
                        help='a url to include in footer of the message')
    parser.add_argument('message',
                        type=util.decode_cli_arg,
                        help='the message content to send')
    return parser.parse_args(argv[1:])


def main(argv):
    """
    pullover's entry point.

    :param argv: Command-line arguments, with the program in position 0.
    """

    args = _parse_argv(argv)

    # sort out logging output and level
    level = util.log_level_from_vebosity(args.verbosity)
    root = logging.getLogger()
    root.setLevel(level)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    handler.setFormatter(logging.Formatter('%(levelname)s %(message)s'))
    root.addHandler(handler)

    logger.debug(args)

    message = Message(args.message, args.title, args.timestamp, args.url,
                      args.priority)
    app = Application(args.app)
    user = User(args.user)
    response = message.send(app, user)
    if response.ok:
        print(response.id)
        return 0

    util.print_error(os.linesep.join(response.errors))
    return 1


def main_cli():
    """
    pullover's command-line entry point.

    :return: The return code of the program.
    """
    status = main(sys.argv)
    logger.debug('Returning exit status %d', status)
    return status


if __name__ == '__main__':
    sys.exit(main_cli())
