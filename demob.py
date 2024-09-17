from algocomponents.tasks import Task


class TaskA(Task):
    pass


class TaskB(Task):
    task = TaskA()


class TaskC(Task):
    pass


task_a = TaskA()
print(task_a.section)  # Prints DEFAULT, DEFAULT is set as THE CONFIG

task_b = TaskB(section="PROD")
print(task_b.section)  # Prints PROD
print(task_b.task.section)  # Also prints DEFAULT

task_c = TaskC()
print(task_c.section)  # This will now also print DEFAULT
