import os
import sys
from configparser import ConfigParser
from datetime import datetime

from common.loggiedoggie import LoggieDoggie
from common.tools import config_to_str
from definitions import GLOBAL_CONFIG


class Task(LoggieDoggie):
    """A generic task which starts using its start()-method

    The task initiates a logger, finds its classpath (where it is located), and
    parses a config file. The log is written to a file in root called log.log,
    and the config file is read from a folder called config, located where this
    class resides. The config is an ini-file, parsed with pythons ConfigParser.
    """

    _default_section = "DEFAULT"

    def __init__(self, config: ConfigParser = None, section: str = None):
        super().__init__()

        self.section = section or self._default_section

        self.classpath = os.path.dirname(sys.modules[self.__class__.__module__].__file__)

        self.config = ConfigParser()
        self.config.optionxform = str  # Preserve casing in config file

        # First read global config
        self.config.read(GLOBAL_CONFIG)

        # Then append or overwrite from config inheritance
        if config:
            for section in config:
                for key, value in config[section].items():
                    self.config[section][key] = value

        # Then append or overwrite from the local config file
        self.config.read(os.path.join(self.classpath, "config/config.ini"))

        self.task_name = type(self).__name__

    def start(self):
        run_start = datetime.now()

        self.logger.info(f"Starting task {self.task_name} "
                         f"with section {self.section}")
        self.logger.info(config_to_str(self.config))

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
        self.config[self.section][key] = value
