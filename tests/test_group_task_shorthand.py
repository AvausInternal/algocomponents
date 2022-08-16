from unittest import TestCase

from algocomponents.adapters import LocalSqliteAdapter
from algocomponents.tasks import GroupTask, SQLPipeline


class EmptySQLPipeline(SQLPipeline):
    pass


class ShorthandGroupTask(GroupTask):
    task_list = [
        EmptySQLPipeline(),
    ]

    sql_adapter = LocalSqliteAdapter()


class TestThatSQLAdaptersConnectAndDisconnectCorrectly(TestCase):
    def test_that_short_hand_group_task_works(self):
        group_task = ShorthandGroupTask()
        assert group_task.sql_adapter is not None
        assert len(group_task.task_list) == 1
        # Cannot assert exact object because of pytest shallow copy
        # We can at least compare adapter types
        assert type(group_task.task_list[0].sql_adapter) == type(group_task.sql_adapter)

    def test_that_short_hand_group_task_accepts_new_adapters(self):
        new_sql_adapter = LocalSqliteAdapter()
        group_task = ShorthandGroupTask(sql_adapter=new_sql_adapter)
        assert group_task.sql_adapter is new_sql_adapter
        assert group_task.task_list[0].sql_adapter is new_sql_adapter
