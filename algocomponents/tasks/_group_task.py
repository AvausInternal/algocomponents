from configparser import ConfigParser
from typing import List

from algocomponents.adapters import SQLAdapter
from algocomponents.tasks import Task


class GroupTask(Task):
    """GroupTask iterates over a list of tasks and starts them."""

    def __init__(
            self,
            task_list: List[Task] = None,
            sql_adapter: SQLAdapter = None,
            config: ConfigParser = None,
            section: str = None,
    ):
        super().__init__(config=config, section=section)
        if task_list:
            self.task_list = task_list
        if not hasattr(self, "task_list"):
            self.task_list = []

        self.instantiated_sql_adapter = False
        if sql_adapter:
            self.sql_adapter = sql_adapter
        elif hasattr(self, "sql_adapter"):
            self.instantiated_sql_adapter = True
        else:
            self.sql_adapter = None

        for task in self.task_list:
            task.parent = self

    def run(self):
        for task in self.task_list:
            task.start()

    def shutdown(self):
        if self.instantiated_sql_adapter:
            self.sql_adapter.disconnect()

    def add_to_config(self, key, value):
        self.config[self.section][key] = str(value)

        for task in self.task_list:
            task.add_to_config(key, value)
