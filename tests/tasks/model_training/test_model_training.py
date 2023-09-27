import os
import shutil

import pandas as pd
import pytest

from algocomponents.adapters import LocalSqliteAdapter
from algocomponents.tasks import LinearRegressionTrainer


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

    def test_training_existing_model_without_overwrite(self):
        if not os.path.exists(self.model_path):
            os.makedirs(self.model_path)
        metadata_file_path = os.path.join(self.model_path, "meta.json")
        with open(metadata_file_path, "w") as file:
            file.write("Nothing")

        self.create_dataset_table(dataset_table=self.double_input_table)
        with pytest.raises(ValueError):
            training_pipeline = LinearRegressionTrainer(
                sql_adapter=self.sql_adapter,
                dataset_table=self.double_input_table,
                target_label_column=self.target_label_column,
                output_path=self.model_path,
                overwrite_existing_model=False,
            )
            training_pipeline.start()

        self.sql_adapter.connect()
        self.sql_adapter.run_sql_string(f"DROP TABLE {self.double_input_table}")
        self.sql_adapter.disconnect()

    def test_excluding_columns_that_do_not_exist(self):
        self.create_dataset_table(dataset_table=self.double_input_table)
        with pytest.raises(ValueError):
            training_pipeline = LinearRegressionTrainer(
                sql_adapter=self.sql_adapter,
                dataset_table=self.double_input_table,
                target_label_column=self.target_label_column,
                output_path=self.model_path,
                excluded_columns=["does_not_exist"],
                overwrite_existing_model=True,
            )
            training_pipeline.start()

        self.sql_adapter.connect()
        self.sql_adapter.run_sql_string(f"DROP TABLE {self.double_input_table}")
        self.sql_adapter.disconnect()

    def test_training_on_non_existent_target_label(self):
        self.create_dataset_table(dataset_table=self.double_input_table)
        with pytest.raises(ValueError):
            training_pipeline = LinearRegressionTrainer(
                sql_adapter=self.sql_adapter,
                dataset_table=self.double_input_table,
                target_label_column="not_in_the_dataset",
                output_path=self.model_path,
            )
            training_pipeline.start()

        self.sql_adapter.connect()
        self.sql_adapter.run_sql_string(f"DROP TABLE {self.double_input_table}")
        self.sql_adapter.disconnect()

    def test_training_real_model(self):
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

        self.sql_adapter.connect()
        self.sql_adapter.run_sql_string(f"DROP TABLE {self.double_input_table}")
        self.sql_adapter.disconnect()
        shutil.rmtree(self.model_path)
