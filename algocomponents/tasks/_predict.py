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
        output_prediction_csv: File path to a csv file of the output.
        output_prediction_column: Column where the model score will be appended.
        excluded_columns: Columns to not use when predicting (for example primary keys)
        overwrite_output: If True, the current output will be overwritten,
            regardless of whether it is a table or a csv.

    """

    def __init__(
        self,
        dataset_table: str,
        target_label_column: str,
        model_path: str,
        output_prediction_table: str = None,
        output_prediction_csv: str = None,
        output_prediction_column: str = "score",
        excluded_columns: List[str] = None,
        overwrite_output: bool = False,
        **kwargs,
    ):
        assert output_prediction_table or output_prediction_csv, (
            "Must supply either a output_prediction_table or an"
            "output_prediction_csv, got neither."
        )
        super().__init__(**kwargs)
        self.dataset_table = dataset_table
        self.target_label_column = target_label_column
        self.model_path = model_path
        self.output_prediction_table = output_prediction_table
        self.output_prediction_csv = output_prediction_csv
        self.output_prediction_column = output_prediction_column
        self.excluded_columns = excluded_columns or []
        self.overwrite_output = overwrite_output
        self.metadata = {}

    def startup(self):
        super().startup()
        self.metadata = self._load_and_validate_metadata()

    def run(self):
        df = self.sql_adapter.table_as_pandas_df(self.dataset_table)
        x = df.drop(columns=self.excluded_columns + [self.target_label_column])

        df = predict_with_model(
            model_path=self.model_path,
            metadata=self.metadata,
            df=x,
            prediction_column=self.output_prediction_column,
        )

        if self.output_prediction_csv:
            if self.overwrite_output and os.path.exists(self.output_prediction_csv):
                os.remove(self.output_prediction_csv)
            df.to_csv(self.output_prediction_csv)
        if self.output_prediction_table:
            self.sql_adapter.pandas_df_as_table(
                df=df,
                table=self.output_prediction_table,
                overwrite=self.overwrite_output,
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
