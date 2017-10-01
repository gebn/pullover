Pullover
========

The simplest Pushover API wrapper for Python, release v\ |version|.

.. image:: https://img.shields.io/pypi/l/pullover.svg
    :target: https://pypi.python.org/pypi/pullover
.. image:: https://img.shields.io/pypi/pyversions/pullover.svg
    :target: https://pypi.python.org/pypi/pullover

Send a message
--------------

To send a message, simply:

   >>> import pullover
   >>> pullover.send('message', 'user', 'app')

You can additionally pass any parameters accepted by
:class:`~pullover.Message`'s initialiser.

.. automodule:: pullover
    :members:
    :undoc-members:

Querying the response
---------------------

:meth:`pullover.send()` returns a :class:`~pullover.message.SendResponse`
object, from which the status, request ID and any errors can be retrieved.

   >>> response = pullover.send('message', 'user', 'app')
   >>> response.ok
   True
   >>> response.id
   5042853c-402d-4a18-abcb-168734a801de
   >>> response.status
   1
   >>> response.errors
   []

If you'd like to use exceptions, :meth:`~pullover.message.SendResponse.raise_for_status()`
will raise either a :class:`~pullover.ClientSendError` or
:class:`~pullover.ServerSendError` if :attr:`~pullover.message.SendResponse.ok`
is ``False``.

.. autoclass:: pullover.message.SendResponse
    :members:

API Documentation
-----------------

.. toctree::
    :maxdepth: 2

    low_level
    exceptions


Indices
-------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
