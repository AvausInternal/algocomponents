import os
import shutil


import pandas as pd
import pytest

from algocomponents.adapters import LocalSqliteAdapter
from algocomponents.tasks import (
    LinearRegressionTrainer,
    ModelEvaluator,
    RandomForestClassifierTrainer,
)


class TestModelEvaluator:
    dataset_table = "test_model_evaluator_dataset"
    target_label_column = "y"
    self_path = os.path.join("tests", "tasks", "model_evaluator")
    model_path = os.path.join(self_path, "model")
    plot_path = os.path.join(self_path, "plots")
    output_table = "model_score_output"

    sql_adapter = LocalSqliteAdapter()

    def create_regression_model(self):
        df = pd.DataFrame()
        input_list = list(range(1, 100))
        df["x"] = input_list
        df[self.target_label_column] = df["x"] * 2

        self.sql_adapter.connect()
        self.sql_adapter.pandas_df_as_table(
            df=df,
            table=self.dataset_table,
            overwrite=True,
        )
        training_pipeline = LinearRegressionTrainer(
            sql_adapter=self.sql_adapter,
            dataset_table=self.dataset_table,
            target_label_column=self.target_label_column,
            output_path=self.model_path,
            overwrite_existing_model=True,
        )
        training_pipeline.start()
        self.sql_adapter.disconnect()

    def create_classification_model(self):
        df = pd.DataFrame()
        input_list = list(range(1, 100))
        df["x"] = input_list
        df[self.target_label_column] = 0
        df.loc[df["x"] > 50, self.target_label_column] = 1

        self.sql_adapter.connect()
        self.sql_adapter.pandas_df_as_table(
            df=df,
            table=self.dataset_table,
            overwrite=True,
        )
        training_pipeline = RandomForestClassifierTrainer(
            sql_adapter=self.sql_adapter,
            dataset_table=self.dataset_table,
            target_label_column=self.target_label_column,
            output_path=self.model_path,
            overwrite_existing_model=True,
        )
        training_pipeline.start()
        self.sql_adapter.disconnect()

    def test_evaluating_regression_model(self):
        self.create_regression_model()

        self.sql_adapter.connect()

        dataset_df = self.sql_adapter.table_as_pandas_df(self.dataset_table)
        model_evaluator = ModelEvaluator(
            sql_adapter=self.sql_adapter,
            dataset_df=dataset_df,
            target_label_column=self.target_label_column,
            model_path=self.model_path,
            model_type="regression",
        )
        model_evaluator.start()

        self.sql_adapter.disconnect()
        shutil.rmtree(self.model_path)

    def test_evaluating_classification_model(self):
        self.create_classification_model()

        self.sql_adapter.connect()

        dataset_df = self.sql_adapter.table_as_pandas_df(self.dataset_table)
        model_evaluator = ModelEvaluator(
            sql_adapter=self.sql_adapter,
            dataset_df=dataset_df,
            target_label_column=self.target_label_column,
            model_path=self.model_path,
            model_type="classification",
        )
        model_evaluator.start()

        self.sql_adapter.disconnect()
        shutil.rmtree(self.model_path)

    def test_incorrect_model_type(self):
        with pytest.raises(ValueError):
            ModelEvaluator(
                sql_adapter=self.sql_adapter,
                dataset_df=pd.DataFrame(),
                target_label_column=self.target_label_column,
                model_path=self.model_path,
                model_type="bad_type",
            )

    def test_incorrect_target_label_column(self):
        with pytest.raises(ValueError):
            ModelEvaluator(
                sql_adapter=self.sql_adapter,
                dataset_df=pd.DataFrame(),
                target_label_column="bad_column",
                model_path=self.model_path,
                model_type="classification",
            )

    def test_drawing_plots(self):
        self.create_classification_model()

        self.sql_adapter.connect()

        dataset_df = self.sql_adapter.table_as_pandas_df(self.dataset_table)
        model_evaluator = ModelEvaluator(
            sql_adapter=self.sql_adapter,
            dataset_df=dataset_df,
            target_label_column=self.target_label_column,
            model_path=self.model_path,
            model_type="classification",
            plot_folder=self.plot_path,
        )
        model_evaluator.start()

        self.sql_adapter.disconnect()
        shutil.rmtree(self.model_path)
        shutil.rmtree(self.plot_path)
