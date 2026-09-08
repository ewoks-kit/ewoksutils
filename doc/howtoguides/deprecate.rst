Deprecate functionality
=======================

Use :func:`ewoksutils.deprecation_utils.deprecated` to deprecate a
function:

.. code-block:: python

    from ewoksutils.deprecation_utils import deprecated


    @deprecated("use new_function instead")
    def old_function():
        ...

Calling ``old_function`` emits a ``DeprecationWarning`` with the given
message.

Use the message to indicate the replacement whenever possible.