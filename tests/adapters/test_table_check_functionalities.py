import pytest

from algocomponents.adapters import LocalSqliteAdapter
from algocomponents.tasks import SQLTask


class TestLocalSqliteAdapterTableMethods:
    sqlite_adapter = LocalSqliteAdapter()

    create_table_query = """DROP TABLE IF EXISTS non_empty_table;

CREATE TABLE non_empty_table (
    what_is_love VARCHAR(255) NOT NULL
    , baby_dont_hurt_me VARCHAR(255) NOT NULL
);

INSERT INTO non_empty_table VALUES ("don't hurt me", "no more");
    """

    create_table_task = SQLTask(
        sql_adapter=sqlite_adapter, sql_string=create_table_query
    )

    def test_table_exists(self):
        self.sqlite_adapter.connect()
        self.create_table_task.start()

        assert self.sqlite_adapter.check_table_has_rows("non_empty_table")
        self.sqlite_adapter.disconnect()
