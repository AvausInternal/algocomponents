import os
import sys
import uuid
from configparser import ConfigParser
from datetime import datetime
from types import ModuleType

from algocomponents.utils import LoggieDoggie, config_to_str, merge_configs


class Task:
    """A generic task which starts using its start()-method.

    The task initiates a logger, finds its classpath (where it is located), and
    parses a config file. The log is written to a file in root called log.log,
    and the config file is read from a folder called config, located where this
    class resides. The config is an ini-file, parsed with pythons ConfigParser.

    Args:
        global_config_dir: Path from project root to global config.ini-file.
        global_config_dir: Relative path to local config.ini-file.
        config: A passed ConfigParser object, which overwrites any files read.
        section: Which section of the ConfigParsers should be read from.

    """

    _default_section = "DEFAULT"

    def __init__(
        self,
        global_config_dir: str = "config",
        local_config_dir: str = "config",
        config: ConfigParser = None,
        section: str = None,
    ):
        self.task_name = type(self).__name__

        self.section = section or self._default_section

        module = sys.modules[self.__class__.__module__]
        if isinstance(module, ModuleType):
            self.classpath = os.path.dirname(module.__file__)
        else:
            self.classpath = ""

        self.config = ConfigParser()
        self.config.optionxform = str  # Preserve casing in config file

        # First read global config
        self.config.read(os.path.join(global_config_dir, "config.ini"))

        # Then append or overwrite from the local config file
        self.config.read(os.path.join(self.classpath, local_config_dir, "config.ini"))

        # Then append or overwrite from a passed config
        if config is not None:
            self.config = merge_configs(
                merge_this=config, into_this=self.config, overwrite=True
            )

        # Set a logger for the task
        self.logger = LoggieDoggie().fetch_logger(
            logger_name=self.task_name,
            config=dict(self.config[self.section]),
        )

        self.run_id = None

        self.parent = None

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
        pass

    def run(self):
        """The tasks main functionality"""
        pass

    def shutdown(self):
        """What the task needs to do after executing it's main funcionality"""
        pass

    def add_to_config(self, key, value):
        """Add values to config for the current section

        Args:
            key: Which key to add or update
            value: What value to give the key

        """
        self.config[self.section][key] = str(value)
