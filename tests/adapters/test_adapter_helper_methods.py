import os

from algocomponents.adapters import LocalSqliteAdapter
from algocomponents.tasks import SQLTask


class TestAdapterHelperMethods:
    sql_adapter = LocalSqliteAdapter(
        global_config_dir=os.path.join("tests", "adapters", "config"),
    )
    columns = ["a", "b"]

    def setup_table(self, table):
        SQLTask(
            sql_string=f"""
                DROP TABLE IF EXISTS {table};

                CREATE TABLE {table} AS
                SELECT
                    1 AS {self.columns[0]},
                    2 AS {self.columns[1]}
            """,
            sql_adapter=self.sql_adapter,
            global_config_dir=os.path.join("tests", "adapters", "config"),
        ).start()

    def test_finding_table_with_templated_variables(self):
        table = "{tmp_db}.find_table_test"
        self.setup_table(table=table)

        self.sql_adapter.connect()
        assert self.sql_adapter.table_exists(table)
        self.sql_adapter.disconnect()

    def test_getting_columns_from_table_with_templated_variables(self):
        table = "{tmp_db}.columns_table_test"
        self.setup_table(table=table)

        self.sql_adapter.connect()
        assert self.sql_adapter.get_table_columns(table) == self.columns
        self.sql_adapter.disconnect()

    def test_table_contains_columns(self):
        table = "{tmp_db}.columns_table_test"
        self.setup_table(table=table)

        self.sql_adapter.connect()
        assert (
            self.sql_adapter.table_contains_columns(
                table=table,
                # Only the first value in columns
                columns=self.columns[:1],
            )
            is True
        )
        assert (
            self.sql_adapter.table_contains_columns(
                table=table,
                # Only the first value in columns
                columns=self.columns[:1],
                identical=True,
            )
            is False
        )
        assert (
            self.sql_adapter.table_contains_columns(
                table=table,
                columns=self.columns,
                identical=True,
            )
            is True
        )
        self.sql_adapter.disconnect()

    def test_format_string_works(self):
        format_variables = {
            "var_one": "one",
            "var_two": "two",
        }
        query = "SELECT {var_one}, {var_two}"
        correct_query = "SELECT one, two"

        formatted_query = self.sql_adapter.get_formatted_queries(
            sql_string=query, format_variables=format_variables
        )[0]
        assert formatted_query == correct_query

        queries = "SELECT {var_one}; SELECT {var_two}"
        correct_queries = ["SELECT one", "SELECT two"]

        formatted_queries = self.sql_adapter.get_formatted_queries(
            sql_string=queries, format_variables=format_variables
        )
        for formatted_query, correct_query in zip(formatted_queries, correct_queries):
            assert formatted_query == correct_query
