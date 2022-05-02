from configparser import ConfigParser
from typing import List

from algocomponents.tasks import Task


class GroupTask(Task):
    """GroupTask iterates over a list of tasks and starts them."""

    def __init__(
            self,
            task_list: List[Task] = None,
            config: ConfigParser = None,
            section: str = None,
    ):
        super().__init__(config=config, section=section)
        self.task_list = task_list or []

    def run(self):
        for task in self.task_list:
            task.start()

    def add_to_config(self, key, value):
        self.config[self.section][key] = str(value)

        for task in self.task_list:
            task.add_to_config(key, value)
