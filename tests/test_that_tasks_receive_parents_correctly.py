from unittest import TestCase

from algocomponents.tasks import Task, GroupTask


class TestThatTasksReceiveParentsCorrectly(TestCase):
    def test_that_simple_task_has_no_parent(self):
        task = Task()
        assert task.parent is None

    def test_that_simple_group_task_has_no_parent(self):
        group_task = GroupTask()
        assert group_task.parent is None

    def test_that_tasks_do_not_have_parents_before_started(self):
        task = Task()
        group_task = GroupTask(task_list=[task])
        assert 0

    def test_that_tasks_receive_a_parent_once_started(self):
        task = Task()
        group_task = GroupTask(task_list=[task])
        group_task.start()
        assert task.parent is group_task

    def test_that_group_task_assigns_parents_for_new_task_list(self):
        task_a = Task()
        task_b = Task()
        group_task = GroupTask(task_list=[task_a])
        group_task.task_list = [task_b]
        group_task.start()
        assert task_a.parent is None
        assert task_b.parent is group_task

    def test_that_parents_assign_correctly_in_nested_tasks(self):
        task_a = Task()
        task_b = Task()
        group_task_a = GroupTask()
        group_task_b = GroupTask()

        group_task_a.task_list = [task_a, group_task_b]
        group_task_b.task_list = [task_b]

        group_task_a.start()

        assert task_a.parent is group_task_a
        assert group_task_b.parent is group_task_a
        assert task_b.parent is group_task_b

    def test_that_parents_are_only_assigned_in_part_of_tree_that_runs(self):
        task_a = Task()
        task_b = Task()
        group_task_a = GroupTask()
        group_task_b = GroupTask()

        group_task_a.task_list = [task_a, group_task_b]
        group_task_b.task_list = [task_b]

        group_task_b.start()

        assert task_a.parent is None
        assert group_task_b.parent is None
        assert task_b.parent is group_task_b
