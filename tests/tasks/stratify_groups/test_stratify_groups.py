import os.path

import pandas as pd
import pytest

from algocomponents.adapters import LocalSqliteAdapter
from algocomponents.adapters.custom_exceptions import (
    DataMismatchException,
    TableIsEmptyException,
)
from algocomponents.tasks import SQLPipeline
from algocomponents.tasks.stratify_groups.stratify_groups import StratifyGroups


class TestStratifyGroups:
    sql_adapter = LocalSqliteAdapter(
        global_config_dir=os.path.join("tests", "tasks", "stratify_groups", "config"),
    )
    stratify_input_table = "{tmp_db}.stratify_input_table"
    stratify_input_table_empty = "{tmp_db}.stratify_input_table_empty"

    def mock_input_table(self, mock_table: str, make_table_empty: bool = False):
        pipeline = SQLPipeline(
            sql_adapter=self.sql_adapter,
            sql_folder=os.path.join("tests", "tasks", "stratify_groups", "sql_setup"),
            sql_folder_relative_path=False,
            global_config_dir=os.path.join(
                "tests", "tasks", "stratify_groups", "config"
            ),
        )
        pipeline.add_to_config("mock_table", mock_table)
        if make_table_empty:
            pipeline.add_to_config("truncate_statement", "LIMIT 0")
        else:
            pipeline.add_to_config("truncate_statement", "")
        pipeline.start()

    def test_stratifying_with_correct_parameters(self):
        self.mock_input_table(mock_table=self.stratify_input_table)
        output_table = "{tmp_db}.stratified_output"
        n_groups = 3
        StratifyGroups(
            sql_adapter=self.sql_adapter,
            input_table=self.stratify_input_table,
            stratify_on=["customer_id", "country", "city"],
            n_groups=n_groups,
            output_table=output_table,
            global_config_dir=os.path.join(
                "tests", "tasks", "stratify_groups", "config"
            ),
        ).start()

        self.sql_adapter.connect()
        assert self.sql_adapter.table_exists(output_table)

        output_df = self.sql_adapter.table_as_pandas_df(output_table)
        assert len(pd.unique(output_df["test_group"])) == n_groups

        self.sql_adapter.disconnect()

    def test_stratifying_into_one_group(self):
        self.mock_input_table(mock_table=self.stratify_input_table)
        output_table = "{tmp_db}.stratified_output"
        n_groups = 1
        StratifyGroups(
            sql_adapter=self.sql_adapter,
            input_table=self.stratify_input_table,
            stratify_on=["customer_id", "country", "city"],
            n_groups=n_groups,
            output_table=output_table,
            global_config_dir=os.path.join(
                "tests", "tasks", "stratify_groups", "config"
            ),
        ).start()

        self.sql_adapter.connect()
        assert self.sql_adapter.table_exists(output_table)

        output_df = self.sql_adapter.table_as_pandas_df(output_table)
        assert len(pd.unique(output_df["test_group"])) == n_groups

        self.sql_adapter.disconnect()

    def test_stratifying_into_zero_groups(self):
        self.mock_input_table(mock_table=self.stratify_input_table)
        output_table = "{tmp_db}.stratified_output"
        n_groups = 0
        StratifyGroups(
            sql_adapter=self.sql_adapter,
            input_table=self.stratify_input_table,
            stratify_on=["customer_id", "country", "city"],
            n_groups=n_groups,
            output_table=output_table,
            global_config_dir=os.path.join(
                "tests", "tasks", "stratify_groups", "config"
            ),
        ).start()

        self.sql_adapter.connect()
        assert self.sql_adapter.table_exists(output_table)
        self.sql_adapter.disconnect()

    def test_stratify_on_non_existing_column(self):
        self.mock_input_table(mock_table=self.stratify_input_table)
        with pytest.raises(DataMismatchException):
            StratifyGroups(
                sql_adapter=self.sql_adapter,
                input_table=self.stratify_input_table,
                stratify_on=["customer_id", "country", "city", "address"],
                n_groups=2,
                output_table="{tmp_db}.stratified_output",
                global_config_dir=os.path.join(
                    "tests", "tasks", "stratify_groups", "config"
                ),
            ).start()

    def test_stratify_on_empty_table(self):
        self.mock_input_table(
            mock_table=self.stratify_input_table, make_table_empty=True
        )
        with pytest.raises(TableIsEmptyException):
            StratifyGroups(
                sql_adapter=self.sql_adapter,
                input_table=self.stratify_input_table,
                stratify_on=["customer_id", "country", "city", "address"],
                n_groups=2,
                output_table="{tmp_db}.stratified_output",
                global_config_dir=os.path.join(
                    "tests", "tasks", "stratify_groups", "config"
                ),
            ).start()

    def test_stratifying_into_more_groups_than_records_in_table(self):
        self.mock_input_table(mock_table=self.stratify_input_table)
        output_table = "{tmp_db}.stratified_output"

        self.sql_adapter.connect()
        input_df = self.sql_adapter.table_as_pandas_df(self.stratify_input_table)
        n_groups = input_df.shape[0] + 1

        StratifyGroups(
            sql_adapter=self.sql_adapter,
            input_table=self.stratify_input_table,
            stratify_on=["customer_id", "country", "city"],
            n_groups=n_groups,
            output_table=output_table,
            global_config_dir=os.path.join(
                "tests", "tasks", "stratify_groups", "config"
            ),
        ).start()

        output_df = self.sql_adapter.table_as_pandas_df(output_table)
        assert output_df.shape[0] == input_df.shape[0]
        assert len(pd.unique(output_df["test_group"])) < n_groups

        self.sql_adapter.disconnect()

    def test_for_empty_table(self):
        self.mock_input_table(
            mock_table=self.stratify_input_table, make_table_empty=True
        )
