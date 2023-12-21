import pytest

from algocomponents.adapters import LocalSqliteAdapter
from algocomponents.tasks import SQLTask


class TestLocalSqliteAdapterTableMethods:
    sqlite_adapter = LocalSqliteAdapter()

    create_table_query = """DROP TABLE IF EXISTS tmp_dream_table;

    CREATE TABLE tmp_dream_table AS
    SELECT
        "downward" AS a_dream,
        "the_way_forward" AS within_a_dream
    ;
    """

    create_table_task = SQLTask(
        sql_adapter=sqlite_adapter, sql_string=create_table_query
    )

    def test_table_exists(self):
        self.create_table_task.start()

        self.create_table_task.sql_adapter.connect()
        assert self.create_table_task.sql_adapter.table_exists("tmp_dream_table")
        assert not self.create_table_task.sql_adapter.table_exists("tmp_reality_table")
        self.create_table_task.sql_adapter.disconnect()

    def test_table_columns(self):
        self.create_table_task.start()

        self.create_table_task.sql_adapter.connect()
        assert self.create_table_task.sql_adapter.get_table_columns(
            "tmp_dream_table"
        ) == ["a_dream", "within_a_dream"]
        self.create_table_task.sql_adapter.disconnect()

    def test_count_rows_in_table(self):
        self.create_table_task.start()
        self.create_table_task.sql_adapter.connect()
        with pytest.raises(Exception) as e_info:
            self.create_table_task.sql_adapter.count_rows_in_table(
                "does_not_exist_table"
            ) == 1

        assert (
            self.create_table_task.sql_adapter.count_rows_in_table("tmp_dream_table")
            == 1
        )
