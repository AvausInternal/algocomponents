from unittest import TestCase

from algocomponents.adapters import LocalSqliteAdapter
from algocomponents.tasks import AdapterTask, GroupTask, Task


class TestThatSQLAdaptersConnectAndDisconnectCorrectly(TestCase):

    sql_adapter = LocalSqliteAdapter()

    def test_that_a_task_has_the_adapter_given_to_it(self):
        task = AdapterTask(sql_adapter=self.sql_adapter)
        assert (task.sql_adapter == self.sql_adapter)

    def test_that_a_group_task_propagates_its_adapter(self):
        task = AdapterTask()
        group_task = GroupTask(task_list=[task], sql_adapter=self.sql_adapter)
        assert (task.sql_adapter == self.sql_adapter)

    def test_that_a_group_task_propagates_its_adapter_when_none_is_passed(self):
        task = AdapterTask(sql_adapter=None)
        group_task = GroupTask(task_list=[task], sql_adapter=self.sql_adapter)
        assert (task.sql_adapter == self.sql_adapter)

    def test_that_a_group_task_does_not_overwrite_adapters(self):
        another_sql_adapter = LocalSqliteAdapter()
        task = AdapterTask(sql_adapter=self.sql_adapter)
        group_task = GroupTask(task_list=[task], sql_adapter=another_sql_adapter)
        assert (task.sql_adapter == self.sql_adapter)

    def test_that_a_group_task_propagates_to_nested_tasks(self):
        task = AdapterTask()
        group_task_a = GroupTask(task_list=[task])
        group_task_b = GroupTask(task_list=[group_task_a], sql_adapter=self.sql_adapter)
        assert (task.sql_adapter == self.sql_adapter)

    def test_that_sql_adapters_do_not_propagate_to_tasks_without_adapters(self):
        task = Task()
        group_task = GroupTask(task_list=[task], sql_adapter=self.sql_adapter)
        assert (not hasattr(task, "sql_adapter"))

    def test_that_group_task_propagates_correctly_in_complex_structure(self):
        sql_adapter_p = LocalSqliteAdapter()
        sql_adapter_q = LocalSqliteAdapter()
        task_a = AdapterTask()
        task_b = AdapterTask(sql_adapter=sql_adapter_p)
        task_c = AdapterTask()
        task_d = AdapterTask(sql_adapter=sql_adapter_q)
        task_e = AdapterTask(sql_adapter=sql_adapter_p)
        task_f = AdapterTask(sql_adapter=sql_adapter_q)
        group_task_x = GroupTask(task_list=[task_a, task_b])
        group_task_y = GroupTask(task_list=[task_c, task_d], sql_adapter=sql_adapter_p)
        group_task_z = GroupTask(task_list=[task_e, task_f], sql_adapter=sql_adapter_q)
        group_task = GroupTask(task_list=[group_task_x, group_task_y, group_task_z], sql_adapter=self.sql_adapter)

        # Task tree for visualization
        # group task, self.sql_adapter
        #   - group_task_x, no adapter
        #       - task_a, no adapter
        #       - task_b, sql_adapter_p
        #   - group_task_y, sql_adapter_p
        #       - task_c, no adapter
        #       - task_d, sql_adapter_q
        #   - group_task_z, sql_adapter_q
        #       - task_e, sql_adapter_p
        #       - task_f, sql_adapter_q

        assert (task_a.sql_adapter == self.sql_adapter)
        assert (task_b.sql_adapter == sql_adapter_p)
        assert (task_c.sql_adapter == sql_adapter_p)
        assert (task_d.sql_adapter == sql_adapter_q)
        assert (task_e.sql_adapter == sql_adapter_p)
        assert (task_f.sql_adapter == sql_adapter_q)
        assert (group_task_x.sql_adapter == self.sql_adapter)
        assert (group_task_y.sql_adapter == sql_adapter_p)
        assert (group_task_z.sql_adapter == sql_adapter_q)
        assert (group_task.sql_adapter == self.sql_adapter)
