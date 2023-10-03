import json
import os
from typing import List

import joblib

from algocomponents.tasks import Task
from algocomponents.utils import predict_with_model


class Predict(Task):
    """Predicts using a model and appends the model score to a dataset table.

    Given a dataset_table as an input, this Task will produce an output table
    that contains everything from the dataset

    Args:
        dataset_table: Full path to table used to predict.
        target_label_column: Name of target label column. This column is excluded
            when making predictions
        model_path: Path to folder with model files.
        output_prediction_table: Full path to where output should be stored.
        output_prediction_column: Column where the model score will be appended.
        excluded_columns: Columns to not use when predicting (for example primary keys)
        overwrite_output_table: If False, the task will raise a TableAlreadyExists
            exception if the output table already exists. Otherwise it is overwritten.

    """

    def __init__(
        self,
        dataset_table: str,
        target_label_column: str,
        model_path: str,
        output_prediction_table: str,
        output_prediction_column: str = "score",
        excluded_columns: List[str] = None,
        overwrite_output_table: bool = False,
        use_probabilistic_predictions: bool = False,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.dataset_table = dataset_table
        self.target_label_column = target_label_column
        self.model_path = model_path
        self.output_prediction_table = output_prediction_table
        self.output_prediction_column = output_prediction_column
        self.excluded_columns = excluded_columns or []
        self.overwrite_output_table = overwrite_output_table
        self.use_probabilistic_predictions = use_probabilistic_predictions
        self.metadata = {}

    def startup(self):
        super().startup()
        self.metadata = self._load_and_validate_metadata()

    def run(self):
        df = self.sql_adapter.table_as_pandas_df(self.dataset_table)

        for excluded_column in self.excluded_columns:
            if excluded_column not in df.columns:
                raise ValueError(
                    f"tried to exclude column {excluded_column} "
                    f"which is not in the dataset:\n{df.head(5)}"
                )

        x = df.drop(columns=self.excluded_columns + [self.target_label_column])

        df = predict_with_model(
            model_path=self.model_path,
            metadata=self.metadata,
            df=x,
            prediction_column=self.output_prediction_column,
            predict_probabilities=self.use_probabilistic_predictions,
        )

        self.sql_adapter.pandas_df_as_table(
            df=df,
            table=self.output_prediction_table,
            overwrite=self.overwrite_output_table,
        )
        self.sql_adapter.disconnect()

    def _load_and_validate_metadata(self):
        metadata_path = os.path.join(self.model_path, "meta.json")
        if not os.path.exists(metadata_path):
            raise FileNotFoundError(
                "Could not find the metadata file, there is probably not a model here: "
                f"{self.model_path}"
            )

        with open(metadata_path, "r") as f:
            metadata = json.load(f)

        if "model_file" not in metadata:
            raise ValueError(
                'Metadata file does not contain key "model_file"\n' f"{metadata}"
            )

        return metadata
