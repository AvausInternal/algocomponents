import os
from unittest import TestCase

from algocomponents.adapters import LocalSqliteAdapter
from algocomponents.tasks.synthesize_table._synthesize_table import SynthesizeTable


class TestUtils(TestCase):
    def test_get_synthesization_query(self):
        adapter = LocalSqliteAdapter()
        adapter.connect()
        adapter.run_sql_file(
            os.path.join(
                "tests",
                "tasks",
                "synthesize_table",
                "synthesization_test_queries",
                "1_create_test_table.sql",
            )
        )
        task = SynthesizeTable(
            input_table="synthesization_test",
            output_table="asd",
            sql_adapter=adapter
        )
        task.get_synthesization_query()
        adapter.disconnect()
