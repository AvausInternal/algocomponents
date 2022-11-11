import os
import sys
from configparser import ConfigParser
from unittest import TestCase

import pandas as pd

from algocomponents.adapters import LocalSqliteAdapter
from algocomponents.tasks import Task


# Need to define class here so that it reads the config/config.ini-file
class EmptyTask(Task):
    pass


class TestAdapterReturningPandasDataframe(TestCase):

    sql_adapter = LocalSqliteAdapter()

    def test_that_list_of_pandas_dataframe_is_returned(self):
        self.sql_adapter.connect()
        df_list = self.sql_adapter.run_sql_string("SELECT 1")
        assert isinstance(df_list, list)
        assert isinstance(df_list[0], pd.DataFrame)
        self.sql_adapter.disconnect()

    def test_that_more_then_one_pandas_dataframe_is_returned(self):
        self.sql_adapter.connect()
        df_list = self.sql_adapter.run_sql_string("SELECT 1; SELECT 2")
        assert len(df_list) == 2
        self.sql_adapter.disconnect()

    def test_that_pandas_dataframe_has_correct_size(self):
        self.sql_adapter.connect()
        module = sys.modules[self.__class__.__module__]
        sql_folder = os.path.join(
            os.path.dirname(module.__file__),
            "test_adapter_returning_pandas_dataframe_queries",
        )
        df_list = self.sql_adapter.run_sql_file(
            os.path.join(sql_folder, "large_query.sql")
        )
        assert df_list[0].shape[0] == 30
        self.sql_adapter.disconnect()

    def test_that_adapters_pick_up_max_rows_displayed_config(self):
        row_limit = 1
        max_one_row_config = ConfigParser()
        max_one_row_config.set(
            section="DEFAULT", option="max_rows_displayed", value=str(row_limit)
        )
        sql_adapter_max_one_row = LocalSqliteAdapter(config=max_one_row_config)
        assert sql_adapter_max_one_row.max_rows_displayed == row_limit

        # Should not affect shape of returned dataframe
        sql_adapter_max_one_row.connect()
        module = sys.modules[self.__class__.__module__]
        sql_folder = os.path.join(
            os.path.dirname(module.__file__),
            "test_adapter_returning_pandas_dataframe_queries",
        )
        df_list = sql_adapter_max_one_row.run_sql_file(
            os.path.join(sql_folder, "large_query.sql")
        )
        assert df_list[0].shape[0] == 30
        sql_adapter_max_one_row.disconnect()

    def test_table_as_pandas_df(self):
        self.sql_adapter.connect()
        module = sys.modules[self.__class__.__module__]
        sql_folder = os.path.join(
            os.path.dirname(module.__file__),
            "test_adapter_returning_pandas_dataframe_queries",
        )
        self.sql_adapter.run_sql_file(
            os.path.join(sql_folder, "table_creation_query.sql")
        )
        df = self.sql_adapter.table_as_pandas_df("test_table_as_pandas")
        assert df.shape[0] == 30

    def test_table_is_empty_empty_table(self):
        self.sql_adapter.connect()
        module = sys.modules[self.__class__.__module__]
        sql_folder = os.path.join(
            os.path.dirname(module.__file__),
            "test_adapter_returning_pandas_dataframe_queries",
        )
        self.sql_adapter.run_sql_file(
            os.path.join(sql_folder, "create_empty_table.sql")
        )
        assert self.sql_adapter.table_is_empty("empty_table")

    def test_table_is_empty_populated_table(self):
        self.sql_adapter.connect()
        module = sys.modules[self.__class__.__module__]
        sql_folder = os.path.join(
            os.path.dirname(module.__file__),
            "test_adapter_returning_pandas_dataframe_queries",
        )
        self.sql_adapter.run_sql_file(
            os.path.join(sql_folder, "table_creation_query.sql")
        )
        assert not self.sql_adapter.table_is_empty("test_table_as_pandas")
