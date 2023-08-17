from algocomponents.tasks import GroupTask, Task


class TestGroupTaskShorthand:
    def test_that_task_has_a_run_id(self):
        task = Task()
        assert task.run_id is None
        task.start()
        assert task.run_id is not None
        assert isinstance(task.run_id, str)
        assert len(task.run_id) > 0

    def test_that_run_ids_propagate(self):
        task = Task()
        group_task = GroupTask(
            task_list=[task],
        )
        assert group_task.run_id is None

        group_task.start()
        assert group_task.run_id is not None
        assert task.run_id == group_task.run_id
