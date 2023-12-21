algocomponents.tasks
====================

The tasks are what you start in order to do anything in algocomponents.

All tasks inherit from the base class ``Task``. ``Task`` defines the ``start()``-method that is used to start any task, and also defines the methods ``startup()``, ``run()`` and ``shutdown()``. These three methods are what other tasks overwrite to perform their respective functions.

Subpackages
-----------

.. toctree::
   :maxdepth: 4

   algocomponents.tasks.check_significance
   algocomponents.tasks.downsample_table
   algocomponents.tasks.evaluate_prediction
   algocomponents.tasks.model_trainers
   algocomponents.tasks.stratify_groups
   algocomponents.tasks.task_verifier

Contents
--------

.. automodule:: algocomponents.tasks
   :members:
   :undoc-members:
   :show-inheritance:
