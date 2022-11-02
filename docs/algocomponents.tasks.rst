algocomponents.tasks
====================

The tasks are what you start in order to do anything in algocomponents.

All tasks inherit from the base class ``Task``. ``Task`` defines the ``start()``-method that is used to start any task, and also defines the methods ``startup()``, ``run()`` and ``shutdown()``. These three methods are what other tasks overwrite to perform their respective functions.

Subpackages
-----------

.. toctree::
   :maxdepth: 4

   algocomponents.tasks.model_evaluator
   algocomponents.tasks.task_verifier

Contents
--------

.. automodule:: algocomponents.tasks
   :members:
   :undoc-members:
   :show-inheritance:
