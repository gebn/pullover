pullover
========

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

    from pullover import Application, User, Message, PulloverError

    try:
        aws = Application('57tn23v578n9887nvh2g5892')
        george = User('8v57nhg578hh5n0h887hh04245')
        message = Message('foo bar', title='hello')
        message.send(aws, george)
    except ValueError:
        # invalid argument
        pass
    except PulloverError:
        # sending error
        pass
