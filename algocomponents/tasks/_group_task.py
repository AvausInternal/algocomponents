from configparser import ConfigParser
from typing import List

from algocomponents.adapters import SQLAdapter
from algocomponents.tasks import Task, AdapterTask


class GroupTask(AdapterTask):
    """GroupTask iterates over a list of tasks and starts them."""

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
