import json
import os
from typing import List

import numpy as np
import pandas as pd
from sklearn.inspection import permutation_importance
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
    confusion_matrix,
)

from algocomponents.tasks import Task, AvausVisuals
from algocomponents.utils import predict_with_model, load_model


class ModelEvaluator(Task):
    """Evaluates a Sci-kit learn model.

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
        output_table: str = None,
        overwrite_output_table: bool = False,
        n_permutation_repeats: int = 5,
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
        if output_table and self.sql_adapter is None:
            raise ValueError(f"sql_adapter is required if an output_table is given")
        self.dataset_df = dataset_df
        self.target_label_column = target_label_column
        self.model_path = model_path
        self.excluded_columns = excluded_columns or []
        self.model_type = model_type
        self.prediction_column = prediction_column
        self.plot_folder = plot_folder
        if output_table:
            self.output_table = self.format_string(output_table)
        else:
            self.output_table = None
        self.overwrite_output_table = overwrite_output_table
        self.n_permutation_repeats = n_permutation_repeats
        self.metadata = {}

    def startup(self):
        super().startup()
        self.metadata = self._load_and_validate_metadata()

    def run(self):
        x = self.dataset_df.drop(
            columns=self.excluded_columns + [self.target_label_column]
        )

        x2 = self.dataset_df.drop(
            columns=self.excluded_columns + [self.target_label_column]
        )

        predict_df = predict_with_model(
            model_path=self.model_path,
            metadata=self.metadata,
            df=x,
            prediction_column=self.prediction_column,
        )

        self.dataset_df[self.prediction_column] = predict_df[self.prediction_column]
        if self.output_table:
            self.sql_adapter.pandas_df_as_table(
                df=self.dataset_df,
                table=self.output_table,
                overwrite=self.overwrite_output_table,
            )

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
            self.logger.info("Confusion matrix:")
            self.logger.info(confusion_matrix(y_test, y_pred))

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

        model = load_model(model_path=self.model_path, metadata=self.metadata)
        r = permutation_importance(
            model, X=x2, y=y_test, n_repeats=self.n_permutation_repeats, random_state=0
        )
        sorted_importances_idx = (-r.importances_mean).argsort()

        importances_df = pd.DataFrame(
            r.importances[sorted_importances_idx].T,
            columns=x2.columns[sorted_importances_idx],
        )

        self.logger.info("Feature importance")
        for feature in sorted_importances_idx:
            self.logger.info(
                f"{x2.columns[feature]:<10}   : {r.importances_mean[feature]:.3f} +/- {r.importances_std[feature]:.3f}"
            )

        if self.plot_folder:
            visualizer = AvausVisuals()
            visualizer.boxplot(
                importances_df,
                title="Permutation importances",
                file_name="permutation_importance_boxplot",
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
