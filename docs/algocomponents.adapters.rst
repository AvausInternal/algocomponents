algocomponents.adapters
=======================

The adapters are what tasks use to connect to database providers.

All adapters inherit from the base class ``SQLAdapter``. All methods you use to interact with an adapter are defined there, like ``connect()``, ``disconnect()``, ``run_sql_string()`` etc.

Most other adapters have helper methods or similar they define, but understanding these are only necessary to understand the internal workings of that adapter. If you are looking to use adapters, reading the documentation for ``SQLAdapter`` is all you need.

Submodules
----------

algocomponents.adapters.custom\_exceptions
------------------------------------------

.. automodule:: algocomponents.adapters.custom_exceptions
   :members:
   :undoc-members:
   :show-inheritance:

Contents
--------

.. automodule:: algocomponents.adapters
   :members:
   :undoc-members:
   :show-inheritance:
