from algocomponents.tasks._task import Task
from algocomponents.tasks._sql_task import SQLTask
from algocomponents.tasks._group_task import GroupTask
from algocomponents.tasks._sql_pipeline import SQLPipeline
from algocomponents.tasks._feature_base import FeatureBase
from algocomponents.tasks._feature import Feature
from algocomponents.tasks._union_tables import UnionTables
from algocomponents.tasks.evaluate_prediction.evaluate_prediction import (
    EvaluatePrediction,
)
from algocomponents.tasks._avaus_visuals import AvausVisuals
from algocomponents.tasks._visualize_dataset import VisualizeDataset
from algocomponents.tasks.check_significance.check_significance import (
    CheckSignificance,
)
from algocomponents.tasks._predict import Predict
from algocomponents.tasks.model_trainers.model_trainer import ModelTrainer
from algocomponents.tasks.model_trainers.linear_regression_trainer import (
    LinearRegressionTrainer,
)
from algocomponents.tasks.model_trainers.random_forest_classifier_trainer import (
    RandomForestClassifierTrainer,
)
from algocomponents.tasks.model_trainers.gradient_boosting_classifier_trainer import (
    GradientBoostingClassifierTrainer,
)
from algocomponents.tasks._visualize_features import (
    VisualizeFeatures,
)
from algocomponents.tasks._data_transfer_task import DataTransferTask

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
    "FeatureBase",
    "Feature",
    "UnionTables",
    "EvaluatePrediction",
    "AvausVisuals",
    "VisualizeDataset",
    "CheckSignificance",
    "Predict",
    "ModelTrainer",
    "LinearRegressionTrainer",
    "RandomForestClassifierTrainer",
    "GradientBoostingClassifierTrainer",
    "VisualizeFeatures",
    "DataTransferTask",
]
