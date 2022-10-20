from typing import List

from algocomponents.tasks import Task, AdapterTask
from algocomponents.utils._tools import merge_configs


class GroupTask(AdapterTask):
    """GroupTask iterates over a list of tasks and starts them.

    GroupTask also keeps its task list up to date with any changes: If
    add_to_config() is called, any addition will also be added to the tasks in
    the task_list (which can themselves be GroupTasks, in which case they will
    do the same). Similarly, any adapter given to a GroupTask will propagate
    down into all tasks in the task list (where GroupTasks in the task_list
    will do the same).

    Tasks in the task_list can be referred to as "children", and they refer to
    the GroupTask as their "parent". All tasks connected this way can be
    referred to as the "task-tree".

    Args:
        task_list: The list of tasks this GroupTask will start

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

        if self.config is not None:
            self.propagate_config()

    def run(self):
        """Iterate through task list and .start() every task

        Also sets the parent of every task into this GroupTask

        """
        for task in self.task_list:
            task.parent = self
            task.start()

    def add_to_config(self, key, value):
        """Recursively add values to config for the current section

        This will also call add_to_config for all tasks in the task_list. As
        those tasks will either inherit from GroupTasks or Tasks, everything in
        the task tree below this task will get these values added.

        Args:
            key: Which key to add or update
            value: What value to give the key

        """
        self.config[self.section][key] = str(value)

        for task in self.task_list:
            task.add_to_config(key, value)

    def set_sql_adapter(self, sql_adapter):
        """Set the SQLAdapter for this GroupTask and all tasks in it's task list

        As all tasks in the task list either inherit from GroupTasks or Tasks,
        everything in the task tree below this task will get this SQLAdapter
        (unless the Task or GroupTask already has an sql_adapter)

        Args:
            sql_adapter: The SQLAdapter to set

        """
        self.sql_adapter = sql_adapter
        self.propagate_sql_adapter(sql_adapter)

    def propagate_sql_adapter(self, sql_adapter):
        """Propagates the SQLAdapter to all tasks in this GroupTasks task_list

        Unless the Task already has an SQLAdapter, this SQLAdapter will be set

        Args:
            sql_adapter: The SQLAdapter to set

        """
        for task in self.task_list:
            if hasattr(task, "sql_adapter"):
                if task.sql_adapter is None:
                    task.set_sql_adapter(sql_adapter)

    def propagate_config(self):
        """Propagates the config to all tasks in this GroupTasks task_list

        This uses the merge_config-method with overwrite as False. This means
        that a GroupTask will never overwrite config-values for tasks in its
        task_list, but for everything that is missing this will set a value.

        """
        for task in self.task_list:
            task.config = merge_configs(
                merge_this=self.config, into_this=task.config, overwrite=False
            )
