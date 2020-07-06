#!/usr/bin/env python
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


class DependencyAction(argparse.Action):
    """
    Ensures that if parameter A is specified, then B is also specified.
    Indicate the `dest` of the required parameter with `depends_on`.
    """

    def __init__(self, option_strings, dest, depends_on, **kwargs):
        super(DependencyAction, self).__init__(option_strings, dest, **kwargs)
        if depends_on is None:
            raise ValueError('Argument must have a dependency')
        self._depends_on = depends_on

    def __call__(self, parser, namespace, values, option_string=None):
        if values and getattr(namespace, self._depends_on) is None:
            parser.error(
                '{0} requires {1} to be specified'.format(option_string,
                                                          self._depends_on))
        setattr(namespace, self.dest, values)


class PriorityAction(argparse.Action):
    """
    Processes the --priority value.
    """

    _PRIORITIES = {
        str(Message.LOWEST): Message.LOWEST,
        'lowest': Message.LOWEST,
        str(Message.LOW): Message.LOW,
        'low': Message.LOW,
        str(Message.NORMAL): Message.NORMAL,
        'normal': Message.NORMAL,
        str(Message.HIGH): Message.HIGH,
        'high': Message.HIGH
    }

    def __call__(self, parser, namespace, values, option_string=None):
        if values not in self._PRIORITIES.keys():
            parser.error("'{0}' is not a recognised priority".format(values))

        setattr(namespace, self.dest, self._PRIORITIES[values])


def _parse_argv(argv):
    """
    Interpret command line arguments.

    :param list(str) argv: `sys.argv`
    :return: The populated argparse namespace.
    :rtype: argparse.Namespace
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
                        env='PUSHOVER_APP_TOKEN',
                        help='the application token to send from; defaults to '
                             'PUSHOVER_APP_TOKEN')
    parser.add_argument('-u', '--user',
                        action=EnvDefault,
                        env='PUSHOVER_USER_KEY',
                        help='the user key to send to; defaults to '
                             'PUSHOVER_USER_KEY')
    parser.add_argument('-p', '--priority',
                        action=PriorityAction,
                        help='the priority of the message, either an integer '
                             "or string (e.g. '0' or 'normal')",
                        default=Message.NORMAL)
    parser.add_argument('-t', '--title',
                        help='the title of the message; defaults to the name '
                             'of the sending application')
    parser.add_argument('--timestamp',
                        type=dateutil.parser.parse,
                        help='the timestamp of the message, in ISO 8601 '
                             'format; defaults to now')
    parser.add_argument('--url',
                        help='a url to include in footer of the message')
    parser.add_argument('--url-title',
                        action=DependencyAction,
                        depends_on='url',
                        help='the URL title; requires --url')
    parser.add_argument('message',
                        help='the message content to send')
    return parser.parse_args(argv[1:])


def main(argv):
    """
    pullover's entry point.

    :param list(str) argv: Command-line arguments, with the program in position
                           0.
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
                      args.url_title, args.priority)
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
    :rtype: int
    """
    status = main(sys.argv)
    logger.debug('Returning exit status %d', status)
    return status


if __name__ == '__main__':
    sys.exit(main_cli())
