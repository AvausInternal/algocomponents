from configparser import ConfigParser
from typing import List

from algocomponents.adapters import SQLAdapter
from algocomponents.tasks import Task, AdapterTask


class GroupTask(AdapterTask):
    """GroupTask iterates over a list of tasks and starts them."""

    def __init__(
            self,
            task_list: List[Task] = None,
            sql_adapter: SQLAdapter = None,
            config: ConfigParser = None,
            section: str = None,
    ):
        super().__init__(
            sql_adapter=sql_adapter,
            config=config,
            section=section,
        )
        if task_list:
            self.task_list = task_list
        if not hasattr(self, "task_list"):
            self.task_list = []

        if sql_adapter:
            self.sql_adapter = sql_adapter
        if not hasattr(self, "sql_adapter"):
            self.sql_adapter = None

    def run(self):
        for task in self.task_list:
            task.parent = self
            task.start()

    def add_to_config(self, key, value):
        self.config[self.section][key] = str(value)

        for task in self.task_list:
            task.add_to_config(key, value)
