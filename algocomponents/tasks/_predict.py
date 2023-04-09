import json
import os
from typing import List

import joblib

from algocomponents.tasks import Task


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
        excluded_columns: List[str] = None,
        overwrite_output_table: bool = False,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.dataset_table = dataset_table
        self.target_label_column = target_label_column
        self.model_path = model_path
        self.output_prediction_table = output_prediction_table
        self.excluded_columns = excluded_columns or []
        self.overwrite_output_table = overwrite_output_table
        self.metadata = {}

    def startup(self):
        super().startup()
        self.metadata = self._load_and_validate_metadata()

    def run(self):
        model_path = os.path.join(self.model_path, self.metadata["model_file"])
        model = joblib.load(filename=model_path)

        self.sql_adapter.connect()
        df = self.sql_adapter.table_as_pandas_df(self.dataset_table)
        x = df.drop(columns=self.excluded_columns + [self.target_label_column])

        if "preprocessor_path" in self.metadata:
            pre_processor_path = os.path.join(
                self.model_path, self.metadata["preprocessor_path"]
            )
            preprocessor = joblib.load(filename=pre_processor_path)
            x = preprocessor.transform(x)

        y_pred = model.predict(x)
        df["score"] = y_pred

        self.sql_adapter.pandas_df_as_table(
            df=df,
            table=self.output_prediction_table,
            overwrite=self.overwrite_output_table,
        )
        self.sql_adapter.disconnect()

    def _load_and_validate_metadata(self):
        metadata_path = os.path.join(self.model_path, "meta.json")
        with open(metadata_path, "r") as f:
            metadata = json.load(f)

        if "model_file" not in metadata:
            raise ValueError(
                'Metadata file does not contain key "model_file"\n' f"{metadata}"
            )

        return metadata
