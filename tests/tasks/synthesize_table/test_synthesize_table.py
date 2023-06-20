import os
from unittest import TestCase

from algocomponents.adapters import LocalSqliteAdapter
from algocomponents.tasks import SynthesizeTable


class TestSynthesizeTable(TestCase):
    setup_sql_path = os.path.join(
        "tests",
        "tasks",
        "synthesize_table",
        "synthesization_test_queries",
        "1_create_test_table.sql",
    )
    input_table = "synthesization_test"
    output_table = "synthesization_output"

    def test_get_synthesization_query(self):
        adapter = LocalSqliteAdapter()
        adapter.connect()
        adapter.run_sql_file(self.setup_sql_path)

        task = SynthesizeTable(
            input_table=self.input_table,
            hash_columns=["c"],
            output_table=self.output_table,
            overwrite=True,
            sql_adapter=adapter,
        )
        query = task.get_synthesization_query()

        assert "ROW_NUMBER" not in query
        assert len(query) > 0
        adapter.disconnect()

    def test_replace_column_with_row_number(self):
        adapter = LocalSqliteAdapter()
        adapter.connect()
        adapter.run_sql_file(self.setup_sql_path)

        task = SynthesizeTable(
            input_table=self.input_table,
            row_number_columns=["b"],
            hash_columns=["c"],
            output_table=self.output_table,
            overwrite=True,
            sql_adapter=adapter,
        )
        query = task.get_synthesization_query()

        assert "ROW_NUMBER" in query
        adapter.disconnect()

    def test_run_synthesization_task(self):
        adapter = LocalSqliteAdapter()
        adapter.connect()
        adapter.run_sql_file(self.setup_sql_path)

        SynthesizeTable(
            input_table=self.input_table,
            hash_columns=["c"],
            output_table=self.output_table,
            overwrite=True,
            sql_adapter=adapter,
        ).start()

        assert adapter.table_exists(self.output_table)
        adapter.disconnect()

    def test_column_types_maintained(self):
        adapter = LocalSqliteAdapter()
        adapter.connect()
        adapter.run_sql_file(self.setup_sql_path)

        SynthesizeTable(
            input_table=self.input_table,
            hash_columns=["c"],
            output_table=self.output_table,
            overwrite=True,
            sql_adapter=adapter,
        ).start()

        assert adapter.table_exists(self.output_table)

        input_table_df = adapter.table_as_pandas_df(self.input_table)
        output_table_df = adapter.table_as_pandas_df(self.output_table)

        assert list(input_table_df.columns) == list(output_table_df.columns)
        assert all(input_table_df.dtypes == output_table_df.dtypes)

        adapter.disconnect()

    def test_overwrite_alters_query(self):
        adapter = LocalSqliteAdapter()
        adapter.connect()
        adapter.run_sql_file(self.setup_sql_path)

        overwrite_query = SynthesizeTable(
            input_table=self.input_table,
            hash_columns=["c"],
            output_table=self.output_table,
            overwrite=True,
            sql_adapter=adapter,
        ).get_synthesization_query()

        non_overwrite_query = SynthesizeTable(
            input_table=self.input_table,
            hash_columns=["c"],
            output_table=self.output_table,
            overwrite=False,
            sql_adapter=adapter,
        ).get_synthesization_query()

        assert "DROP TABLE" in overwrite_query
        assert "DROP TABLE" not in non_overwrite_query

        adapter.disconnect()

    def test_that_n_rows_changes(self):
        adapter = LocalSqliteAdapter()
        adapter.connect()
        adapter.run_sql_file(self.setup_sql_path)

        SynthesizeTable(
            input_table=self.input_table,
            hash_columns=["c"],
            output_table=self.output_table,
            overwrite=True,
            sql_adapter=adapter,
            max_rows=3,
        ).start()

        assert adapter.count_rows_in_table(self.output_table) == 3

        SynthesizeTable(
            input_table=self.input_table,
            hash_columns=["c"],
            output_table=self.output_table,
            overwrite=True,
            sql_adapter=adapter,
            max_values_per_column=1,
        ).start()

        # With only 1 value from each column, only 1 row is possible
        assert adapter.count_rows_in_table(self.output_table) == 1

        SynthesizeTable(
            input_table=self.input_table,
            hash_columns=["c"],
            output_table=self.output_table,
            overwrite=True,
            sql_adapter=adapter,
            max_values_per_column=2,
        ).start()

        # Everything is cross joined, and there are three calues
        assert adapter.count_rows_in_table(self.output_table) == 2 * 2 * 2

        SynthesizeTable(
            input_table=self.input_table,
            hash_columns=["c"],
            output_table=self.output_table,
            overwrite=True,
            sql_adapter=adapter,
            max_values_per_column=2,
            max_rows=5,
        ).start()

        assert adapter.count_rows_in_table(self.output_table) == 5

        adapter.disconnect()
