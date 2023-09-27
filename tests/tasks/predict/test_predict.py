import os
import shutil
from unittest import TestCase

import pandas as pd
import pytest

from algocomponents.adapters import LocalSqliteAdapter
from algocomponents.tasks import Predict, LinearRegressionTrainer


class TestPredict(TestCase):
    """Assumes ModelTraining works

    If tests are failing here it might be because ModelTraining does not work.
    Predict relies on there being a model to use for predicting, so they are
    also created in this class.
    """

    double_input_table = "double_input"
    target_label_column = "y"
    model_path = os.path.join("tests", "tasks", "predict", "model")
    output_table = "model_score_output"

    sql_adapter = LocalSqliteAdapter()

    def create_real_model(self):
        self.create_dataset_table(dataset_table=self.double_input_table)
        training_pipeline = LinearRegressionTrainer(
            sql_adapter=self.sql_adapter,
            dataset_table=self.double_input_table,
            target_label_column=self.target_label_column,
            output_path=self.model_path,
            overwrite_existing_model=True,
        )
        training_pipeline.start()

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

    def test_predicting_when_model_is_missing(self):
        with pytest.raises(FileNotFoundError):
            Predict(
                sql_adapter=self.sql_adapter,
                dataset_table=self.double_input_table,
                target_label_column=self.target_label_column,
                model_path="Nowhere",
                output_prediction_table=self.output_table,
                overwrite_output=True,
            ).start()

    def test_predicting_without_output(self):
        with pytest.raises(ValueError):
            Predict(
                sql_adapter=self.sql_adapter,
                dataset_table=self.double_input_table,
                target_label_column=self.target_label_column,
                model_path=self.model_path,
            ).start()

    def test_predicting_with_bad_metadata_file(self):
        if not os.path.exists(self.model_path):
            os.makedirs(self.model_path)
        metadata_file_path = os.path.join(self.model_path, "meta.json")
        with open(metadata_file_path, "w") as file:
            file.write("Nothing")

        with pytest.raises(ValueError):
            Predict(
                sql_adapter=self.sql_adapter,
                dataset_table=self.double_input_table,
                target_label_column=self.target_label_column,
                model_path=self.model_path,
                output_prediction_table=self.output_table,
                overwrite_output=True,
            ).start()

        shutil.rmtree(self.model_path)

    def test_excluding_columns_that_do_not_exist(self):
        self.create_real_model()

        with pytest.raises(ValueError):
            Predict(
                sql_adapter=self.sql_adapter,
                dataset_table=self.double_input_table,
                excluded_columns=["does_not_exist"],
                target_label_column=self.target_label_column,
                model_path=self.model_path,
                output_prediction_table=self.output_table,
                overwrite_output=True,
            ).start()

        shutil.rmtree(self.model_path)

    def test_predicting_to_csv_that_exists(self):
        self.create_real_model()
        csv_file_path = os.path.join(self.model_path, "model_output.csv")

        with open(csv_file_path, "w") as file:
            file.write("Nothing")

        with pytest.raises(ValueError):
            Predict(
                sql_adapter=self.sql_adapter,
                dataset_table=self.double_input_table,
                target_label_column=self.target_label_column,
                model_path=self.model_path,
                output_prediction_csv=csv_file_path,
            ).start()

        shutil.rmtree(self.model_path)

    def test_predicting_with_real_model_to_table(self):
        self.create_real_model()

        Predict(
            sql_adapter=self.sql_adapter,
            dataset_table=self.double_input_table,
            target_label_column=self.target_label_column,
            model_path=self.model_path,
            output_prediction_table=self.output_table,
            overwrite_output=True,
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
        self.sql_adapter.disconnect()

    def test_predicting_with_real_model_to_csv(self):
        self.create_real_model()
        csv_file_path = os.path.join(self.model_path, "model_output.csv")

        Predict(
            sql_adapter=self.sql_adapter,
            dataset_table=self.double_input_table,
            target_label_column=self.target_label_column,
            model_path=self.model_path,
            output_prediction_csv=csv_file_path,
            overwrite_output=True,
        ).start()

        assert os.path.isfile(csv_file_path)

        with open(csv_file_path, "r") as file:
            csv_headers = file.readline()
        assert "score" in csv_headers

        shutil.rmtree(self.model_path)

    def test_predicting_with_real_model_to_table_and_csv(self):
        self.create_real_model()
        csv_file_path = os.path.join(self.model_path, "model_output.csv")

        Predict(
            sql_adapter=self.sql_adapter,
            dataset_table=self.double_input_table,
            target_label_column=self.target_label_column,
            model_path=self.model_path,
            output_prediction_table=self.output_table,
            output_prediction_csv=csv_file_path,
            overwrite_output=True,
        ).start()

        self.sql_adapter.connect()
        assert self.sql_adapter.table_exists(table=self.output_table)
        assert self.sql_adapter.table_contains_columns(
            table=self.output_table,
            columns=["score"],
        )
        assert self.sql_adapter.count_rows_in_table(table=self.output_table) > 0

        self.sql_adapter.run_sql_string(f"DROP TABLE {self.output_table}")
        self.sql_adapter.disconnect()

        assert os.path.isfile(csv_file_path)

        with open(csv_file_path, "r") as file:
            csv_headers = file.readline()
        assert "score" in csv_headers

        shutil.rmtree(self.model_path)
