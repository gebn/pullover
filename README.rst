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

Installation
------------

::

    $ pip install pullover

Demo
----

.. code-block:: python

    from pullover import Application, User, Message, SendError


    # high-level API

    response = pullover.send('foo bar', title='hello', 'user key', 'app token')
    if response.ok:
        print(response.id)  # 647d2300-702c-4b38-8b2f-d56326ae460b


    # low-level API

    try:
        aws = Application('app token')
        george = User('user key')
        message = Message('foo bar', title='hello')
        response = message.send(aws, george)
        response.raise_for_status()
        print(response.id)  # 647d2300-702c-4b38-8b2f-d56326ae460b
    except ClientSendError as e:
        # it was our fault
        print(e.status, e.errors)
    except ServerSendError:
        # Pushover is having issues
        print(e.response.text)
