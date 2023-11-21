import pytest

from algocomponents.adapters import LocalSqliteAdapter
import pandas as pd


class TestAdapterFindTableNames:
    sql_adapter = LocalSqliteAdapter()

    def test_that_running_empty_string_raises_value_error(self):
        with pytest.raises(ValueError):
            self.sql_adapter.connect()
            self.sql_adapter.run_sql_string("")

    def test_that_running_whitespace_string_raises_value_error(self):
        with pytest.raises(ValueError):
            self.sql_adapter.connect()
            self.sql_adapter.run_sql_string("\n\n\t    ")

    def test_that_running_correct_query_produces_no_error(self):
        self.sql_adapter.connect()

        df_list = self.sql_adapter.run_sql_string("SELECT 1")

        assert type(df_list) is list
        assert type(df_list[0]) is pd.DataFrame

        self.sql_adapter.disconnect()
