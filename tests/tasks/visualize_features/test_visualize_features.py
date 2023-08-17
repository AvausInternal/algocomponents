import os.path
import shutil
import pytest

import pandas as pd

from algocomponents.adapters import LocalSqliteAdapter
from algocomponents.adapters.custom_exceptions import (
    ColumnMissingException,
    TableMissingException,
)
from algocomponents.tasks import VisualizeFeatures


class TestVisualizeFeatures:
    """Test VisualizeFeatures class"""

    output_folder = os.path.join(
        "tests", "tasks", "visualize_categorical_features", "plots"
    )
    input_table = "categorical_features_test"
    input_table_df = pd.DataFrame(
        data={
            "cat_1": ["a", "b", "c", "a", "b", "c", "a", "b", "c"],
            "cat_2": ["p", "q", "q", "p", "q", "p", "p", "p", "q"],
            "cont_1": [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9],
            "cont_2": [0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1],
            "target_label": [0, 1, 1, 0, 1, 0, 1, 1, 0],
        }
    )
    sql_adapter = LocalSqliteAdapter()

    def test_with_correct_input(self):
        self.sql_adapter.connect()
        self.sql_adapter.pandas_df_as_table(
            df=self.input_table_df, table=self.input_table, overwrite=True
        )
        categorical_feature_columns = ["cat_1", "cat_2"]
        continuous_feature_columns = ["cont_1", "cont_2"]
        VisualizeFeatures(
            sql_adapter=self.sql_adapter,
            input_table=self.input_table,
            target_label_column="target_label",
            categorical_feature_columns=categorical_feature_columns,
            continuous_feature_columns=continuous_feature_columns,
            output_folder=self.output_folder,
        ).start()
        for col in categorical_feature_columns:
            output_file = os.path.join(self.output_folder, f"{col}.png")
            assert os.path.isfile(output_file)
            os.remove(output_file)
        shutil.rmtree(self.output_folder)
        self.sql_adapter.disconnect()

    def test_with_missing_table(self):
        self.sql_adapter.connect()
        with pytest.raises(TableMissingException):
            VisualizeFeatures(
                sql_adapter=self.sql_adapter,
                input_table="A table that does not exist",
                target_label_column="target_label",
                categorical_feature_columns=[],
                continuous_feature_columns=[],
                output_folder=self.output_folder,
            ).start()
        self.sql_adapter.disconnect()

    def test_with_missing_columns(self):
        self.sql_adapter.connect()
        self.sql_adapter.pandas_df_as_table(
            df=self.input_table_df, table=self.input_table, overwrite=True
        )
        missing_columns = ["missing"]
        with pytest.raises(ColumnMissingException):
            VisualizeFeatures(
                sql_adapter=self.sql_adapter,
                input_table=self.input_table,
                target_label_column="target_label",
                categorical_feature_columns=missing_columns,
                continuous_feature_columns=[],
                output_folder=self.output_folder,
            ).start()
        missing_columns = ["missing"]
        with pytest.raises(ColumnMissingException):
            VisualizeFeatures(
                sql_adapter=self.sql_adapter,
                input_table=self.input_table,
                target_label_column="target_label",
                categorical_feature_columns=[],
                continuous_feature_columns=missing_columns,
                output_folder=self.output_folder,
            ).start()
        self.sql_adapter.disconnect()

    def test_with_duplicate_columns(self):
        self.sql_adapter.connect()
        self.sql_adapter.pandas_df_as_table(
            df=self.input_table_df, table=self.input_table, overwrite=True
        )
        bad_categorical_columns = ["cat_1", "cat_1"]
        bad_continuous_columns = ["cont_1", "cont_1"]
        with pytest.raises(ValueError):
            VisualizeFeatures(
                sql_adapter=self.sql_adapter,
                input_table=self.input_table,
                target_label_column="target_label",
                categorical_feature_columns=bad_categorical_columns,
                continuous_feature_columns=[],
                output_folder=self.output_folder,
            ).start()
        with pytest.raises(ValueError):
            VisualizeFeatures(
                sql_adapter=self.sql_adapter,
                input_table=self.input_table,
                target_label_column="target_label",
                categorical_feature_columns=[],
                continuous_feature_columns=bad_continuous_columns,
                output_folder=self.output_folder,
            ).start()
        self.sql_adapter.disconnect()
