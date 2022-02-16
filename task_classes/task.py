import configparser
import os
import sys
from datetime import datetime

from common.loggiedoggie import LoggieDoggie


class Task(LoggieDoggie):
    """A generic task which starts using its start()-method

    The task initiates a logger, finds its classpath (where it is located), and
    parses a config file. The log is written to a file in root called log.log,
    and the config file is read from a folder called config, located where this
    class resides. The config is an ini-file, parsed with pythons ConfigParser.
    """

    def __init__(self):
        super().__init__()

        self.classpath = os.path.dirname(sys.modules[self.__class__.__module__].__file__)

        self.config = configparser.ConfigParser()
        self.config.optionxform = str  # Preserve casing in config file
        self.config.read(os.path.join(self.classpath, "config/config.ini"))

        self.task_name = type(self).__name__

    def start(self):
        run_start = datetime.now()

        self.logger.info(f"Starting task {self.task_name}")

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
