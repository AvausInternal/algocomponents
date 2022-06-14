import os
import sys
from configparser import ConfigParser
from datetime import datetime
from types import ModuleType

from algocomponents.utils import LoggieDoggie, config_to_str


class Task(LoggieDoggie):
    """A generic task which starts using its start()-method

    The task initiates a logger, finds its classpath (where it is located), and
    parses a config file. The log is written to a file in root called log.log,
    and the config file is read from a folder called config, located where this
    class resides. The config is an ini-file, parsed with pythons ConfigParser.
    """

    _default_section = "DEFAULT"

    def __init__(
            self,
            config: ConfigParser = None,
            section: str = None,
    ):
        self.task_name = type(self).__name__
        super().__init__(logger_name=self.task_name)

        self.section = section or self._default_section

        module = sys.modules[self.__class__.__module__]
        if isinstance(module, ModuleType):
            self.classpath = os.path.dirname(module.__file__)
        else:
            self.classpath = ""

        self.config = ConfigParser()
        self.config.optionxform = str  # Preserve casing in config file

        # First read global config
        self.config.read(os.path.join("config", "config.ini"))

        # Then append or overwrite from config inheritance
        if config:
            for section in config:
                if section not in self.config.keys():
                    self.config.add_section(section)
                for key, value in config[section].items():
                    self.config[section][key] = value

        # Then append or overwrite from the local config file
        self.config.read(os.path.join(self.classpath, "config", "config.ini"))

        log_level = self.config[self.section]["log_level"]

        if log_level not in self.log_levels.keys():
            raise AttributeError(
                f"Tried to set log level to {log_level} which is not in {list(self.log_levels.keys())}"
            )

        self.set_log_level(self.log_levels[log_level])

        self.parent = None

    def start(self):
        run_start = datetime.now()

        self.logger.info(f"Starting task {self.task_name} "
                         f"with section {self.section}")
        self.logger.debug(config_to_str(self.config))

        self.startup()
        self.run()
        self.shutdown()

        now = datetime.now()
        self.logger.info(f"Task {self.task_name} finished after {now - run_start}")

    def startup(self):
        pass

    def run(self):
        pass

    def shutdown(self):
        pass

    def add_to_config(self, key, value):
        self.config[self.section][key] = str(value)
