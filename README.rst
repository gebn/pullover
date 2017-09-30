pullover
========

.. image:: https://img.shields.io/pypi/status/pullover.svg
   :target: https://pypi.python.org/pypi/pullover
.. image:: https://img.shields.io/pypi/v/pullover.svg
   :target: https://pypi.python.org/pypi/pullover
.. image:: https://img.shields.io/pypi/pyversions/pullover.svg
   :target: https://pypi.python.org/pypi/pullover
.. image:: https://travis-ci.org/gebn/pullover.svg?branch=master
   :target: https://travis-ci.org/gebn/pullover
.. image:: https://coveralls.io/repos/github/gebn/pullover/badge.svg?branch=master
   :target: https://coveralls.io/github/gebn/pullover?branch=master

The simplest Pushover API wrapper for Python.

Features
--------

- No extraneous requests - just sends non-emergency messages quickly and without fuss
- Aims to get the basics right, and be open to extension for more advanced use cases
- Timeouts and automatic back-off should Pushover be experiencing issues
- Intuitive command-line interface with sane, parseable output
- Unit and integration tested
- Signed PyPi releases

Limitations
-----------

Pullover does not support:

- Anything other than sending messages
- Sending messages to a subset of a user's devices
- Emergency messages
- Customising the notification sound

If you need one of these, I'd recommend using Karan Lyons's Chump_ wrapper.

.. _Chump: https://github.com/karanlyons/chump

Installation
------------

::

    $ pip install pullover

Module
-------

The following code snippets demonstrate the main features of pullover.

High-level
~~~~~~~~~~

.. code-block:: python

    import pullover

    response = pullover.send('message', 'user key', 'app token')
    if response.ok:
        print(response.id)  # 647d2300-702c-4b38-8b2f-d56326ae460b

Low-level
~~~~~~~~~

.. code-block:: python

    from pullover import Application, User, Message, ClientSendError, \
        ServerSendError

    try:
        aws = Application('app token')
        george = User('user key')
        message = Message('message', title='hello')
        response = message.send(aws, george)
        response.raise_for_status()
        print(response.id)  # 647d2300-702c-4b38-8b2f-d56326ae460b
    except ClientSendError as e:
        # it was our fault
        print(e.status, e.errors)
    except ServerSendError:
        # Pushover is having issues
        print(e.response.text)

CLI
---

The CLI supports the same functionality as the library.

::

    $ pullover -a <app_token> -u <user_key> hello!
    647d2300-702c-4b38-8b2f-d56326ae460b
    $ export PUSHOVER_APP_TOKEN=token
    $ export PUSHOVER_USER_KEY=key
    $ pullover hello!
    647d2300-702c-4b38-8b2f-d56326ae460b
    $ pullover --help
    usage: pullover [-h] [-V] [-v] -a APP -u USER [-p PRIORITY] [-t TITLE]
                    [--timestamp TIMESTAMP] [--url URL] [--url-title URL_TITLE]
                    message

    The simplest Pushover API wrapper for Python.

    positional arguments:
      message               the message content to send

    optional arguments:
      -h, --help            show this help message and exit
      -V, --version         show program's version number and exit
      -v, --verbosity       increase output verbosity
      -a APP, --app APP     the application token to send from; defaults to
                            PUSHOVER_APP_TOKEN
      -u USER, --user USER  the user key to send to; defaults to PUSHOVER_USER_KEY
      -p PRIORITY, --priority PRIORITY
                            the priority of the message, either an integer or
                            string (e.g. '0' or 'normal')
      -t TITLE, --title TITLE
                            the title of the message; defaults to the name of the
                            sending application
      --timestamp TIMESTAMP
                            the timestamp of the message, in ISO 8601 format;
                            defaults to now
      --url URL             a url to include in footer of the message
      --url-title URL_TITLE
                            the URL title; requires --url
