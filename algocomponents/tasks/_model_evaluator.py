import json
import os
from typing import Dict
from typing import List

import numpy as np
import pandas as pd
from sklearn.metrics import (
    precision_score,
    recall_score,
    f1_score,
    accuracy_score,
    r2_score,
    mean_absolute_error,
    mean_squared_error,
    precision_recall_curve,
    roc_auc_score,
)

from algocomponents.tasks import Task, AvausVisuals
from algocomponents.utils import predict_with_model
from algocomponents.utils._tools import shuffle_columns


class ModelEvaluator(Task):
    """Evaluates a Sci-kit learn model

    Given a dataset_table as an input, this Task will evaluate and log model
    performance.

    Args:
        dataset_df: A dataframe of a dataset the model can use to predict.
        target_label_column: Name of target label column. This column is excluded
            when making predictions
        model_path: Path to folder with model files.
        model_type: What type of model es evaluated: classification or regression
        prediction_column: In what column to store the predicted values
        excluded_columns: Columns to not use when predicting (for example primary keys)
        plot_folder: Where to put plots. If no value is sent, plots are not created.

    """

    def __init__(
        self,
        dataset_df: pd.DataFrame,
        target_label_column: str,
        model_path: str,
        model_type: str,
        prediction_column: str = "score",
        plot_folder: str = None,
        excluded_columns: List[str] = None,
        **kwargs,
    ):
        if model_type not in ["classification", "regression"]:
            raise ValueError(
                'model_type must be either "classification" or "regression"'
            )
        if target_label_column not in dataset_df.columns:
            raise ValueError(
                f"Target label column {target_label_column} not found in dataset_df columns: {dataset_df.columns}"
            )
        super().__init__(**kwargs)
        self.dataset_df = dataset_df
        self.target_label_column = target_label_column
        self.model_path = model_path
        self.excluded_columns = excluded_columns or []
        self.model_type = model_type
        self.prediction_column = prediction_column
        self.plot_folder = plot_folder
        self.metadata = {}

    def startup(self):
        super().startup()
        self.metadata = self._load_and_validate_metadata()

    def run(self):
        x = self.dataset_df.drop(
            columns=self.excluded_columns + [self.target_label_column]
        )

        predict_df = predict_with_model(
            model_path=self.model_path,
            metadata=self.metadata,
            df=x,
            prediction_column=self.prediction_column,
        )

        self.dataset_df[self.prediction_column] = predict_df[self.prediction_column]

        y_test = self.dataset_df[self.target_label_column]
        y_pred = self.dataset_df[self.prediction_column]

        if self.model_type == "regression":
            self.logger.info("MAE : %.3f", mean_absolute_error(y_test, y_pred))
            self.logger.info("RMSE: %.3f", np.sqrt(mean_squared_error(y_test, y_pred)))
            self.logger.info("R^2 : %.3f", r2_score(y_test, y_pred))
        elif self.model_type == "classification":
            self.logger.info("Accuracy:  %.3f" % accuracy_score(y_test, y_pred))
            self.logger.info("F1:        %.3f" % f1_score(y_test, y_pred))
            self.logger.info("Precision: %.3f" % precision_score(y_test, y_pred))
            self.logger.info("Recall:    %.3f" % recall_score(y_test, y_pred))

        if self.plot_folder and self.model_type == "classification":
            precision, recall, thresholds = precision_recall_curve(y_test, y_pred)
            auc_score = roc_auc_score(y_test, y_pred)
            df = pd.DataFrame(zip(precision, recall), columns=["Precision", "Recall"])

            visualizer = AvausVisuals()
            visualizer.lineplot(
                df=df,
                x_col="Recall",
                y_col="Precision",
                title=f"AUC Score: {auc_score}",
                file_name="precision_recall_curve",
                output_folder=self.plot_folder,
                show=False,
            )

            shuffled_df = shuffle_columns(
                df=x,
                columns=x.columns,
            )

            auc_changes_df = pd.DataFrame()

            for feature_column in x.columns:
                x_permutation = x.drop(feature_column, axis=1)
                x_permutation[feature_column] = shuffled_df[feature_column]

                new_predict_df = predict_with_model(
                    model_path=self.model_path,
                    metadata=self.metadata,
                    df=x_permutation,
                    prediction_column=self.prediction_column,
                )

                new_y_pred = new_predict_df[self.prediction_column]
                new_auc_score = roc_auc_score(y_test, new_y_pred)

                auc_changes_df[feature_column] = [auc_score - new_auc_score]

            visualizer.barplot(
                df=auc_changes_df,
                x_cols=auc_changes_df.columns,
                file_name="feature_importances",
                output_folder=self.plot_folder,
                show=False,
            )

    def _load_and_validate_metadata(self):
        metadata_path = os.path.join(self.model_path, "meta.json")
        with open(metadata_path, "r") as f:
            metadata = json.load(f)

        if "model_file" not in metadata:
            raise ValueError(
                'Metadata file does not contain key "model_file"\n' f"{metadata}"
            )

        return metadata
