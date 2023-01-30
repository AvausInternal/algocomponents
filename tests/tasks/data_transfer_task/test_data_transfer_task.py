from unittest import TestCase
import os
import pytest

from algocomponents.tasks._data_transfer_task import DataTransferTask
from algocomponents.adapters._local_sqlite_adapter import LocalSqliteAdapter
from algocomponents.tasks._sql_task import SQLTask


@pytest.fixture(scope="class")
def data_transfer_setup():
    # Create local table to transfer data from
    SQLTask(
        sql_file_path=os.path.join(
            "tests/tasks/data_transfer_task/sql/create_local_table.sql"
        ),
        sql_adapter=LocalSqliteAdapter(),
    ).start()
    yield  # runs tests
    SQLTask(
        sql_string="DROP TABLE IF EXISTS data_transfer_table;",
        sql_adapter=LocalSqliteAdapter(),
    ).start()


@pytest.mark.usefixtures("data_transfer_setup")
class TestDataTransferTask(TestCase):
    """Test DataTransferTask"""

    def test_new_table_is_created(self):
        SQLTask(
            sql_string="DROP TABLE IF EXISTS data_transfer_table_new;",
            sql_adapter=LocalSqliteAdapter(),
        ).start()

        DataTransferTask(
            from_adapter=LocalSqliteAdapter(),
            to_adapter=LocalSqliteAdapter(),
            from_table="data_transfer_table",
            to_table="data_transfer_table_new",
            overwrite=True,
        ).start()

        sql_adapter = LocalSqliteAdapter()
        sql_adapter.connect()
        assert sql_adapter.table_exists("data_transfer_table_new")
        assert sql_adapter.table_is_empty("data_transfer_table_new") == False

    def test_new_table_from_query_results_is_created(self):
        SQLTask(
            sql_string="DROP TABLE IF EXISTS data_transfer_table_new;",
            sql_adapter=LocalSqliteAdapter(),
        ).start()

        DataTransferTask(
            sql_string="""SELECT 1 FROM data_transfer_table """,
            from_adapter=LocalSqliteAdapter(),
            to_adapter=LocalSqliteAdapter(),
            to_table="data_transfer_table_new",
            overwrite=True,
        ).start()

        sql_adapter = LocalSqliteAdapter()
        sql_adapter.connect()
        assert sql_adapter.table_exists("data_transfer_table_new")
        assert sql_adapter.table_is_empty("data_transfer_table_new") == False

    def test_correct_data_output(self):
        SQLTask(
            sql_string="DROP TABLE IF EXISTS data_transfer_table_new;",
            sql_adapter=LocalSqliteAdapter(),
        ).start()

        DataTransferTask(
            from_adapter=LocalSqliteAdapter(),
            to_adapter=LocalSqliteAdapter(),
            from_table="data_transfer_table",
            to_table="data_transfer_table_new",
            overwrite=True,
        ).start()

        sql_adapter = LocalSqliteAdapter()
        sql_adapter.connect()
        assert sql_adapter.table_contains_columns(
            "data_transfer_table_new", columns=["adapter", "power_level"]
        )
        assert sql_adapter.table_is_empty("data_transfer_table_new") == False
        sql_adapter.disconnect()
