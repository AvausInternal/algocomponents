from abc import ABC, abstractmethod
from algofactory.abstract_tasks.task import Task
from typing import List


class GroupTask(Task, ABC):
    """GroupTask iterates over a list of tasks and starts them."""

    task_name = "group_task"
    
    @property
    @abstractmethod
    def task_list(self) -> List[Task]:
        return []

    def run(self):
        for task in self.task_list:
            task.start()

