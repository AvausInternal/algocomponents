import os
import shutil


import pandas as pd

from algocomponents.adapters import LocalSqliteAdapter
from algocomponents.tasks import Predict, LinearRegressionTrainer


class TestModelTraining:
    double_input_table = "double_input"
    target_label_column = "y"
    model_path = os.path.join("tests", "tasks", "model_training", "model")
    output_table = "model_score_output"

    sql_adapter = LocalSqliteAdapter()

    def create_dataset_table(self, dataset_table):
        df = pd.DataFrame()
        input_list = list(range(1, 100))
        df["x"] = input_list
        df[self.target_label_column] = df["x"] * 2

        self.sql_adapter.connect()
        self.sql_adapter.pandas_df_as_table(
            df=df,
            table=dataset_table,
            overwrite=True,
        )
        self.sql_adapter.disconnect()

    def test_training_and_predicting(self):
        self.create_dataset_table(dataset_table=self.double_input_table)
        training_pipeline = LinearRegressionTrainer(
            sql_adapter=self.sql_adapter,
            dataset_table=self.double_input_table,
            target_label_column=self.target_label_column,
            output_path=self.model_path,
            overwrite_existing_model=True,
        )
        training_pipeline.start()

        assert os.path.isdir(self.model_path)
        assert os.path.isfile(
            os.path.join(self.model_path, training_pipeline.metadata_file)
        )
        assert os.path.isfile(
            os.path.join(self.model_path, training_pipeline.model_file)
        )
        assert os.path.isfile(
            os.path.join(self.model_path, training_pipeline.preprocessor_file)
        )

        Predict(
            sql_adapter=self.sql_adapter,
            dataset_table=self.double_input_table,
            target_label_column=self.target_label_column,
            model_path=self.model_path,
            output_prediction_table=self.output_table,
            overwrite_output_table=True,
        ).start()

        self.sql_adapter.connect()
        assert self.sql_adapter.table_exists(table=self.output_table)
        assert self.sql_adapter.table_contains_columns(
            table=self.output_table,
            columns=["score"],
        )
        assert self.sql_adapter.count_rows_in_table(table=self.output_table) > 0

        self.sql_adapter.run_sql_string(f"DROP TABLE {self.output_table}")
        shutil.rmtree(self.model_path)
