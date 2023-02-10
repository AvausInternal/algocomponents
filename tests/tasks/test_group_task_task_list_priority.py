from unittest import TestCase

from algocomponents.tasks import GroupTask, Task


class GroupTaskWithTaskList(GroupTask):
    task_list = [
        Task(),
    ]


class TestGroupTaskListPriority(TestCase):
    def test_that_task_list_is_used(self):
        group_task = GroupTaskWithTaskList()
        assert len(group_task.task_list) == 1

    def test_that_task_list_can_be_overwritten(self):
        group_task = GroupTaskWithTaskList(task_list=[Task(), Task(),])
        assert len(group_task.task_list) == 2
