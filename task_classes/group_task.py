from algofactory.task_classes.task import Task
from typing import List


class GroupTask(Task):
    """GroupTask iterates over a list of tasks and starts them."""

    def __init__(self, task_list: List[Task] = None):
        super().__init__()
        self.task_list = task_list or []

    def run(self):
        for task in self.task_list:
            task.start()
