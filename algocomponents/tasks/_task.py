import uuid
from datetime import datetime
from typing import Dict

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

        if self.parent:
            self.run_id = self.parent.run_id
        else:
            self.run_id = str(uuid.uuid1())

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

    def set_sql_adapter(self, sql_adapter):
        """Set the SQLAdapter for this Task

        This is implemented as a method in order for GroupTasks to recursively
        set_sql_adapter in a task-tree.

        Args:
            sql_adapter: The SQLAdapter to set.

        """
        self.sql_adapter = sql_adapter

    def format_with_config(self, string: str, max_depth: int = 5) -> str:
        """Calls .format() on a string with the config of this task.

        To support multiple layers of templated variables, format is called
        multiple times until the string no longer changes. A max depth is used
        to prevent infinite recursion, for example caused by the config:

        {"a": "{b}", "b": "{a}"}

        Which would format "{a}" into "{b}", which formats into "{a}", etc.

        There are more general solutions without a max_depth variable, but the
        added code complexity for these solutions was deemed to not be worth it.

        Args:
            string: The string to format.
            max_depth: Max number of times .format() will be done.

        Returns:
            The provided string, formatted.

        Raises:
            RecursionError: When .format():ing more than max_depth times and the
                string is still changing

        Examples:
            {output_table} -> {tmp_db}.output_table -> tmp.output_table

        """
        previous_string = ""
        depth = 0
        while string != previous_string:
            previous_string = string
            string = string.format(**self.config[self.section])
            depth += 1
            if depth > max_depth:
                raise RecursionError(
                    f"Reached max reformatting depth of {max_depth} with:\n"
                    f"string:\n{string}\n"
                    f"previous_string:\n{previous_string}"
                )
        return string
