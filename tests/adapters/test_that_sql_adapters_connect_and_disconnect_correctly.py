from unittest import TestCase

from algocomponents.adapters import LocalSqliteAdapter
from algocomponents.tasks import Task, GroupTask


class TestThatSQLAdaptersConnectAndDisconnectCorrectly(TestCase):

    sql_adapter = LocalSqliteAdapter()

    def test_that_an_adapter_task_works_with_none_adapter(self):
        task = Task(sql_adapter=None)
        task.start()
        assert task.sql_adapter is None

    def test_that_an_adapter_task_does_not_connect_the_adapter_right_away(self):
        task = Task(sql_adapter=self.sql_adapter)
        assert not task.sql_adapter.is_connected()

    def test_that_an_adapter_connects_after_connecting(self):
        task = Task(sql_adapter=self.sql_adapter)
        task.sql_adapter.connect()
        assert task.sql_adapter.is_connected()

    def test_that_an_adapter_connects_after_running_sql(self):
        task = Task(sql_adapter=self.sql_adapter)
        task.sql_adapter.run_sql_string("SELECT 1")
        assert task.sql_adapter.is_connected()

    def test_that_an_adapter_task_disconnects_its_adapter(self):
        task = Task(sql_adapter=self.sql_adapter)
        task.sql_adapter.connect()
        task.shutdown()
        assert not task.sql_adapter.is_connected()

    def test_that_an_adapter_disconnects_in_a_flow(self):
        task = Task(sql_adapter=self.sql_adapter)
        group_task = GroupTask(task_list=[task])
        task.parent = group_task
        task.sql_adapter.connect()
        group_task.start()
        assert not task.sql_adapter.is_connected()

    def test_that_an_adapter_does_not_disconnect_a_shared_adapter(self):
        task = Task(sql_adapter=self.sql_adapter)
        group_task = GroupTask(task_list=[task], sql_adapter=self.sql_adapter)
        task.parent = group_task
        task.sql_adapter.connect()
        task.shutdown()
        assert task.sql_adapter.is_connected()

    def test_that_an_adapter_disconnects_when_parent_has_no_adapter(self):
        task = Task(sql_adapter=self.sql_adapter)
        group_task = GroupTask(task_list=[task])
        task.parent = group_task
        task.sql_adapter.connect()
        task.shutdown()
        assert not task.sql_adapter.is_connected()

    def test_that_an_adapter_disconnects_when_parent_has_another_adapter(self):
        another_sql_adapter = LocalSqliteAdapter()
        task = Task(sql_adapter=self.sql_adapter)
        group_task = GroupTask(task_list=[task], sql_adapter=another_sql_adapter)
        task.parent = group_task
        task.sql_adapter.connect()
        task.shutdown()
        assert not task.sql_adapter.is_connected()
