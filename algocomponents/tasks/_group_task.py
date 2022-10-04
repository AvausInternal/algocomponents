from typing import List

from algocomponents.tasks import Task, AdapterTask


class GroupTask(AdapterTask):
    """GroupTask iterates over a list of tasks and starts them.

    GroupTask also keeps its task list up to date with any changes: If
    add_to_config() is called, any addition will also be added to the tasks in
    the task_list (which can themselves be GroupTasks, in which case they will
    do the same). Similarly, any adapter given to a GroupTask will propagate
    down into all tasks in the task list (where GroupTasks in the task_list
    will do the same).
    """

    def __init__(
        self,
        task_list: List[Task] = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        if task_list:
            self.task_list = task_list
        if not hasattr(self, "task_list"):
            self.task_list = []

        if self.sql_adapter is not None:
            self.propagate_sql_adapter(self.sql_adapter)

    def run(self):
        for task in self.task_list:
            task.parent = self
            task.start()

    def add_to_config(self, key, value):
        self.config[self.section][key] = str(value)

        for task in self.task_list:
            task.add_to_config(key, value)

    def set_sql_adapter(self, sql_adapter):
        self.sql_adapter = sql_adapter
        self.propagate_sql_adapter(sql_adapter)

    def propagate_sql_adapter(self, sql_adapter):
        for task in self.task_list:
            if hasattr(task, "sql_adapter"):
                if task.sql_adapter is None:
                    task.set_sql_adapter(sql_adapter)
