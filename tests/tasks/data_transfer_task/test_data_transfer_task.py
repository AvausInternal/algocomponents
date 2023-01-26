from unittest import TestCase
import os

from algocomponents.tasks._data_transfer_task import DataTransferTask
from algocomponents.adapters._local_sqlite_adapter import LocalSqliteAdapter
from algocomponents.tasks._sql_task import SQLTask
from algocomponents.config_reader import ConfigReader


class TestDataTransferTask(TestCase):
    """Test DataTransferTask"""

    # Create local table we want to transfer data from
    SQLTask(
        sql_file_path=os.path.join(
            "tests/tasks/data_transfer_task/sql/create_local_table.sql"
        ),
        sql_adapter=LocalSqliteAdapter(),
    ).start()

    def test_new_table_is_created(self):

        SQLTask(
            sql_string="DROP TABLE IF EXISTS data_transfer_table_new;",
            sql_adapter=LocalSqliteAdapter(),
        ).start()

        DataTransferTask(
            sql_string="""SELECT * FROM data_transfer_table """,
            from_adapter=LocalSqliteAdapter(),
            to_adapter=LocalSqliteAdapter(),
            from_table="data_transfer_table",
            to_table="data_transfer_table_new",
            overwrite=True,
        ).start()

        sql_adapter = LocalSqliteAdapter()
        sql_adapter.connect()
        assert sql_adapter.table_exists("data_transfer_table_new")

    def test_correct_data_output(self):

        DataTransferTask(
            sql_string="""SELECT * FROM data_transfer_table """,
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
