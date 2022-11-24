from algocomponents.tasks._task import Task
from algocomponents.tasks._adapter_task import AdapterTask
from algocomponents.tasks._sql_task import SQLTask
from algocomponents.tasks._group_task import GroupTask
from algocomponents.tasks._sql_pipeline import SQLPipeline
from algocomponents.tasks._feature_base import FeatureBase
from algocomponents.tasks._feature import Feature
from algocomponents.tasks._union_tables_task import UnionTablesTask
from algocomponents.tasks.model_evaluator.model_evaluator import ModelEvaluator
from algocomponents.tasks._visualize_dataset import VisualizeDataset
from algocomponents.tasks.check_significance._check_significance_task import (
    CheckSignificanceTask,
)

"""Allows classes to live in separate files while keeping imports short

All the classes are imported into this init-file, and from this file they can
then be imported from the __all__-list, which defines which modules are
available in this package. Note that the modules in the __all__-list must be in
order of dependency: As GroupTask inherits from Task, Task must precede it.
"""

__all__ = [
    "Task",
    "AdapterTask",
    "SQLTask",
    "GroupTask",
    "SQLPipeline",
    "FeatureBase",
    "Feature",
    "UnionTablesTask",
    "ModelEvaluator",
    "VisualizeDataset",
    "CheckSignificanceTask",
]
