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

    row_limit = 1
    max_one_row_config = ConfigParser()
    max_one_row_config.set(
        section="DEFAULT", option="max_rows_returned", value=str(row_limit)
    )

    sql_adapter = LocalSqliteAdapter()
    sql_adapter_max_one_row = LocalSqliteAdapter(config=max_one_row_config)

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
        assert df_list[0].shape[0] == self.sql_adapter.default_max_rows_returned
        self.sql_adapter.disconnect()

    def test_that_pandas_dataframe_size_adjusts_with_config(self):
        self.sql_adapter_max_one_row.connect()
        module = sys.modules[self.__class__.__module__]
        sql_folder = os.path.join(
            os.path.dirname(module.__file__),
            "test_adapter_returning_pandas_dataframe_queries",
        )
        df_list = self.sql_adapter_max_one_row.run_sql_file(
            os.path.join(sql_folder, "large_query.sql")
        )
        assert df_list[0].shape[0] == self.row_limit
        self.sql_adapter_max_one_row.disconnect()
