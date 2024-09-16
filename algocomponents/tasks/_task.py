import uuid
from datetime import datetime

from algocomponents.adapters import SQLAdapter
from algocomponents.config_reader import ConfigReader
from algocomponents.utils import config_to_str


class Task(ConfigReader):
    """A generic task which starts using its start()-method.

    A task has access to an adapter if one is given, and starts with it's
    start()-method. This class is intended to use either when basic operations
    straight towards an adapter are needed as tasks, or to be inherited by more
    fleshed out classes.

    Args:
        sql_adapter: The adapter the task will use.

    """

    _sql_adapter = None  # Global SQL Adapter used

    def __init__(self, sql_adapter: SQLAdapter = None, **kwargs):
        super().__init__(**kwargs)

        self.task_name = self.class_name
        self.run_id = None
        self.parent = None
        self.i_connected_the_adapter = False

        if sql_adapter:
            self.sql_adapter = sql_adapter
            if Task._sql_adapter is None:
                Task._sql_adapter = sql_adapter
        else:
            self.sql_adapter = Task._sql_adapter

    def start(self):
        """Starts the task

        This is the method to use when starting a task. This method will init
        the logger, time the task, and call the three following methods:

            startup()
            run()
            shutdown()

        The above methods are the methods other tasks will use to implement
        their respective functionality.

        """
        run_start = datetime.now()

        self.logger.info(f"Starting task {self.task_name} with section {self.section}")
        self.logger.debug(config_to_str(self.config))

        self.startup()
        self.run()
        self.shutdown()

        now = datetime.now()
        self.logger.info(f"Task {self.task_name} finished after {now - run_start}")

        return self

    def startup(self):
        """What the task needs to do before executing it's main functionality"""
        if self.parent:
            self.run_id = self.parent.run_id
        else:
            self.run_id = str(uuid.uuid1())

        if self.sql_adapter and not self.sql_adapter.is_connected():
            self.i_connected_the_adapter = True
            self.sql_adapter.connect()

    def run(self):
        """The tasks main functionality"""
        pass

    def shutdown(self):
        """What the task should do after having executed it's main functionality

        If this adapter connected the adapter, it should also disconnect it.
        This rule is all-encompassing for handling connecting and disconnecting
        adapters in trees: GroupTasks connect their adapters before passing them
        to their child tasks, so being the task that connects the adapter is the
        same as being the root task in a task tree.

        """
        if self.i_connected_the_adapter:
            self.sql_adapter.disconnect()

    def set_section(self, section):
        """Set the section for this Task

        This is implemented as a method in order for GroupTasks to recursively
        set_section in a task-tree.

        Args:
            section: The section to set.
        Raises:
            ValueError: If the section is not in the config

        """
        self.verify_section_is_in_config(section)
        self.section = section

    def set_sql_adapter(self, sql_adapter):
        """Set the SQLAdapter for this Task

        This is implemented as a method in order for GroupTasks to recursively
        set_sql_adapter in a task-tree.

        Args:
            sql_adapter: The SQLAdapter to set.

        """
        self.sql_adapter = sql_adapter
