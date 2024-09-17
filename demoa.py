from algocomponents.tasks import Task


class TaskA(Task):
    pass


class TaskB(Task):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.task = TaskA()


class TaskC(Task):
    pass


task_a = TaskA()
print(task_a.section)  # Prints DEFAULT

task_b = TaskB(section="PROD")
print(task_b.section)  # Prints PROD
print(task_b.task.section)  # Also prints PROD

task_c = TaskC(section="DEFAULT")
print(task_c.section)  # Prints DEFAULT

task_a = TaskA()
print(task_a.section)  # Prints PROD

