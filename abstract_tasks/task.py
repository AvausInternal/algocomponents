import configparser
import logging
import os
import sys
from abc import ABC, abstractmethod
from datetime import datetime


class Task(ABC):
    """A generic task which starts using its start()-method

    The task initiates a logger, finds its classpath (where it is located), and
    parses a config file. The log is written to a file in root called log.log,
    and the config file is read from a folder called config, located where this
    class resides. The config is an ini-file, parsed with pythons ConfigParser.
    """

    def __init__(self):
        self.logger = self.__get_logger()

        self.classpath = os.path.dirname(sys.modules[self.__class__.__module__].__file__)

        self.config = configparser.ConfigParser()
        self.config.optionxform = str  # Preserve casing in config file
        self.config.read(os.path.join(self.classpath, "config/config.ini"))

    @property
    @abstractmethod
    def task_name(self):
        pass

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

    def __get_logger(self):
        logging.basicConfig(filename="log.log")

        logger = logging.getLogger(f"{self.task_name}_log")
        logger.setLevel(logging.INFO)

        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)

        logger.addHandler(handler)

        return logger
