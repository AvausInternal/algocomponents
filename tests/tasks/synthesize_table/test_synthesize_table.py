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

        adapter.run_sql_string(f"DROP TABLE {self.output_table}")
        adapter.disconnect()

    def test_that_hashing_maintains_column_types(self):
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

        input_column_set = set(input_table_df["c"].tolist())
        output_column_set = set(output_table_df["c"].tolist())
        assert input_column_set != output_column_set

        assert list(input_table_df.columns) == list(output_table_df.columns)
        assert all(input_table_df.dtypes == output_table_df.dtypes)

        adapter.run_sql_string(f"DROP TABLE {self.output_table}")
        adapter.disconnect()

    def test_that_row_number_columns_work(self):
        adapter = LocalSqliteAdapter()
        adapter.connect()
        adapter.run_sql_file(self.setup_sql_path)

        SynthesizeTable(
            input_table=self.input_table,
            row_number_columns=["b"],
            output_table=self.output_table,
            overwrite=True,
            sql_adapter=adapter,
        ).start()

        assert adapter.table_exists(self.output_table)

        input_table_df = adapter.table_as_pandas_df(self.input_table)
        output_table_df = adapter.table_as_pandas_df(self.output_table)

        # Can't really test anything else: Due to randomness, we cannot check
        # highest or lowest value in this column. With bad luck, the "b"-column
        # could theoretically be all 5's for example.
        assert input_table_df["b"].to_list() != output_table_df["b"].to_list()

        adapter.run_sql_string(f"DROP TABLE {self.output_table}")
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
            max_values_per_column=2,
            max_rows=5,
        ).start()

        assert adapter.count_rows_in_table(self.output_table) == 5

        adapter.run_sql_string(f"DROP TABLE {self.output_table}")
        adapter.disconnect()
