import os
from unittest import TestCase

from algocomponents.adapters import LocalSqliteAdapter
from algocomponents.tasks import SQLTask


class TestAdapterHelperMethods(TestCase):

    sql_adapter = LocalSqliteAdapter(
        global_config_dir=os.path.join("tests", "adapters", "config"),
    )

    def test_finding_table_with_templated_variables(self):
        table = "{tmp_db}.find_table_test"
        SQLTask(
            sql_string=f"""
                DROP TABLE IF EXISTS {table};

                CREATE TABLE {table} AS SELECT 1
            """,
            sql_adapter=self.sql_adapter,
            global_config_dir=os.path.join("tests", "adapters", "config"),
        ).start()

        self.sql_adapter.connect()
        assert self.sql_adapter.table_exists(table)
        self.sql_adapter.connect()
