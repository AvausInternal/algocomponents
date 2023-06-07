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

    def __init__(self, sql_adapter: SQLAdapter = None, **kwargs):
        super().__init__(**kwargs)

        self.task_name = self.class_name
        self.run_id = None
        self.parent = None
        self.i_started_the_adapter = False

        if sql_adapter:
            self.sql_adapter = sql_adapter
        if not hasattr(self, "sql_adapter"):
            self.sql_adapter = None

    def start(self):
        """Starts the task

        This is the method to use when starting a task. This method will call
        the three following methods in order:

            startup()
            run()
            shutdown()

        The above methods are the methods other tasks overwrite with their own
        functionality. For a Task, all of these three methods are blank.

        """
        run_start = datetime.now()

        self.logger.info(
            f"Starting task {self.task_name} " f"with section {self.section}"
        )
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
            self.i_started_the_adapter = True
            self.sql_adapter.connect()

    def run(self):
        """The tasks main functionality"""
        pass

    def shutdown(self):
        """Disconnects the sql_adapter, if no other task will use it.

        We will try to disconnect if we have an adapter and it is connected.

        We disconnect if either of these are true:
            - There is no parent.
            - The parent does not have an sql_adapter.
            - The parent does not have the same sql_adapter.

        In other words: Disconnect unless we share the adapter with our parent.

        The most common scenario is that one sql_adapter is used throughout a
        GroupTask: It passes it's sql_adapter to all it's children. Since that
        GroupTasks shutdown() is the last method to run, and it is the only task
        that does not have a parent, the last thing that happens is that the
        sql_adapter is disconnected.

        However, more complicated setups are supported, where as parts of a
        task-tree have their own adapters.

        """
        if self.i_started_the_adapter:
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
