Low-level API
=============

The high-level API exposes the same functionality as the low-level API in a
simpler way, hiding the creation and interaction of various objects.

Applications
------------

.. autoclass:: pullover.Application
    :members:
    :special-members: __init__
    :exclude-members: sign

Users
-----

.. autoclass:: pullover.User
    :members:
    :special-members: __init__
    :exclude-members: sign

Messages
--------

.. autoclass:: pullover.Message
    :members:
    :undoc-members:
    :special-members: __init__

Prepared messages
~~~~~~~~~~~~~~~~~

If you want your :class:`~pullover.Message`, :class:`~pullover.Application` and
:class:`~pullover.User` creation logic to be separate from your sending logic,
prepared messages may help. These are essentially just a tuple containing all
three objects, that you can call :meth:`~pullover.PreparedMessage.send()` on
when ready.

.. autoclass:: pullover.PreparedMessage
    :members:
