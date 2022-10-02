import os
import sys
from unittest import TestCase

import pytest

from algocomponents.adapters import LocalSqliteAdapter
from algocomponents.adapters.custom_exceptions import DataMismatchException
from algocomponents.tasks import UnionTablesTask, SQLTask


class TestUnionTables(TestCase):

    sql_adapter = LocalSqliteAdapter()

    def test_empty_table_list(self):
        with pytest.raises(ValueError):
            UnionTablesTask(
                tables=[], output_table="the_triforce", sql_adapter=self.sql_adapter
            )

    def test_unioning_tables(self):
        module = sys.modules[self.__class__.__module__]
        sql_folder = os.path.join(
            os.path.dirname(module.__file__),
            "test_union_tables_task_sql",
        )
        SQLTask(
            sql_file_path=os.path.join(sql_folder, "setup.sql"),
            sql_adapter=self.sql_adapter,
        ).start()
        union_tables_task = UnionTablesTask(
            tables=[
                "triforce_of_power",
                "triforce_of_wisdom",
                "triforce_of_courage",
            ],
            output_table="the_triforce",
            sql_adapter=self.sql_adapter,
        )
        union_tables_task.start()
        self.sql_adapter.connect()
        assert self.sql_adapter.table_exists("the_triforce")
        assert not self.sql_adapter.table_is_empty("the_triforce")
        self.sql_adapter.disconnect()

    def test_unioning_non_matching_tables(self):
        module = sys.modules[self.__class__.__module__]
        sql_folder = os.path.join(
            os.path.dirname(module.__file__),
            "test_union_tables_task_sql",
        )
        SQLTask(
            sql_file_path=os.path.join(sql_folder, "setup.sql"),
            sql_adapter=self.sql_adapter,
        ).start()
        union_tables_task = UnionTablesTask(
            tables=[
                "triforce_of_courage",
                "light_arrows",
            ],
            output_table="inventory",
            sql_adapter=self.sql_adapter,
        )

        with pytest.raises(DataMismatchException):
            union_tables_task.start()
