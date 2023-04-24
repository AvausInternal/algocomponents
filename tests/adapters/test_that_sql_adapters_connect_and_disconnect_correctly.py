from unittest import TestCase

from algocomponents.adapters import LocalSqliteAdapter
from algocomponents.tasks import Task, GroupTask


class TestThatSQLAdaptersConnectAndDisconnectCorrectly(TestCase):
    def test_that_an_adapter_task_works_with_none_adapter(self):
        task = Task(sql_adapter=None)
        task.start()
        assert task.sql_adapter is None

    def test_that_an_adapter_task_does_not_connect_the_adapter_right_away(self):
        sql_adapter = LocalSqliteAdapter()
        task = Task(sql_adapter=sql_adapter)
        assert not task.sql_adapter.is_connected()
        task.sql_adapter.disconnect()

    def test_that_an_adapter_connects_after_connecting(self):
        sql_adapter = LocalSqliteAdapter()
        task = Task(sql_adapter=sql_adapter)
        task.sql_adapter.connect()
        assert task.sql_adapter.is_connected()
        task.sql_adapter.disconnect()

    def test_that_an_adapter_task_disconnects_its_adapter(self):
        sql_adapter = LocalSqliteAdapter()
        task = Task(sql_adapter=sql_adapter)
        task.startup()
        task.shutdown()
        assert not task.sql_adapter.is_connected()

    def test_that_a_flow_does_not_disconnect_a_connected_adapter(self):
        sql_adapter = LocalSqliteAdapter()
        task = Task(sql_adapter=sql_adapter)
        group_task = GroupTask(task_list=[task])
        task.parent = group_task
        task.sql_adapter.connect()
        group_task.start()
        assert task.sql_adapter.is_connected()
        task.sql_adapter.disconnect()

    def test_that_an_adapter_does_not_disconnect_a_shared_adapter(self):
        sql_adapter = LocalSqliteAdapter()
        task = Task(sql_adapter=sql_adapter)
        group_task = GroupTask(task_list=[task], sql_adapter=sql_adapter)
        task.parent = group_task
        group_task.startup()
        task.startup()
        task.shutdown()
        assert task.sql_adapter.is_connected()
        group_task.sql_adapter.disconnect()

    def test_that_an_adapter_disconnects_when_parent_has_no_adapter(self):
        sql_adapter = LocalSqliteAdapter()
        task = Task(sql_adapter=sql_adapter)
        group_task = GroupTask(task_list=[task])
        task.parent = group_task
        task.startup()
        task.shutdown()
        assert not task.sql_adapter.is_connected()

    def test_that_an_adapter_disconnects_when_parent_has_another_adapter(self):
        sql_adapter = LocalSqliteAdapter()
        another_sql_adapter = LocalSqliteAdapter()
        task = Task(sql_adapter=sql_adapter)
        group_task = GroupTask(task_list=[task], sql_adapter=another_sql_adapter)
        task.parent = group_task
        task.startup()
        task.shutdown()
        assert not task.sql_adapter.is_connected()
