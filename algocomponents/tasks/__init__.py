import imp
from algocomponents.tasks._task import Task
from algocomponents.tasks._sql_task import SQLTask
from algocomponents.tasks._group_task import GroupTask
from algocomponents.tasks._sql_pipeline import SQLPipeline
from algocomponents.tasks.model_evaluator._model_evaluator import ModelEvaluator
"""Allows classes to live in separate files while keeping imports short

All the classes are imported into this init-file, and from this file they can
then be imported from the __all__-list, which defines which modules are
available in this package. Note that the modules in the __all__-list must be in
order of dependency: As GroupTask inherits from Task, Task must precede it.
"""

__all__ = [
    "Task",
    "SQLTask",
    "GroupTask",
    "SQLPipeline",
    "ModelEvaluator",
]
