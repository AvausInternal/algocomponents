import json
import os
import shutil
from typing import List

import joblib
from sklearn.base import BaseEstimator
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

from algocomponents.tasks import Task


class ModelTrainer(Task):
    model_file = "model.joblib"
    preprocessor_file = "preprocessor.joblib"
    metadata_file = "meta.json"

    def __init__(
        self,
        dataset_table: str,
        target_label_column: str,
        output_path: str,
        model_type: str,
        model_reference: BaseEstimator,  # Any scikit learn model
        categorical_columns: List[str] = None,
        excluded_columns: List[str] = None,
        overwrite_existing_model: bool = False,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.dataset_table = dataset_table
        self.target_label_column = target_label_column
        self.output_path = output_path
        self.model_type = model_type
        self.model_reference = model_reference
        self.categorical_columns = categorical_columns or []
        self.excluded_columns = excluded_columns or []
        self.overwrite_existing_model = overwrite_existing_model

    def run(self):
        model, preprocessor = self._create_model()

        self._save_model(model, preprocessor)

    def _create_model(self):
        df = self.sql_adapter.table_as_pandas_df(self.dataset_table)
        df = df.drop(columns=self.excluded_columns)

        preprocessor = ColumnTransformer(
            transformers=[("cat", OneHotEncoder(), self.categorical_columns)],
            remainder="passthrough",
        )
        model = Pipeline(
            steps=[
                ("preprocessor", preprocessor),
                (self.model_type, self.model_reference),
            ]
        )

        model.fit(
            X=df.drop(columns=self.target_label_column),
            y=df[self.target_label_column],
        )

        return model, preprocessor

    def _save_model(self, model, preprocessor):
        if self.overwrite_existing_model:
            if os.path.exists(self.output_path):
                if os.path.isfile(self.output_path):
                    os.remove(self.output_path)
                else:
                    shutil.rmtree(self.output_path)
        os.mkdir(self.output_path)

        joblib.dump(
            value=model, filename=os.path.join(self.output_path, self.model_file)
        )
        joblib.dump(
            value=preprocessor,
            filename=os.path.join(self.output_path, self.preprocessor_file),
        )

        metadata = {
            "model_file": self.model_file,
            "preprocessor_file": self.preprocessor_file,
        }
        metadata_path = os.path.join(self.output_path, self.metadata_file)
        with open(metadata_path, "w+") as f:
            json.dump(metadata, f)
