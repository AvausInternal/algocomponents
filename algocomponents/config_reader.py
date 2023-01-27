import os
import sys
import uuid
from abc import ABC
from configparser import ConfigParser
from datetime import datetime
from types import ModuleType

from algocomponents.utils import LoggieDoggie, config_to_str, merge_configs


class ConfigReader(ABC):
    """A class used to read and manage configs

    The config files are python config.ini-files. The priority is as follows,
    starting with the highest priority (in terms of what overwrites what):

        1. Adding to config via code
        2. Passed config
        3. Local config
        4. Global config

    The rule of thumb is "Code over files, specific beats general".

    The class also creates a unique logger which can be used by classes that
    inherit from this class. The log is by default written to a file in root
    called log.log and printed to the terminal. The log is configurable by these
    fields in the config:

    log_to_file: True or False, decides where a log should be written to file
    log_level: At what level to log (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    Args:
        global_config_dir: Path from project root to global config.ini-file.
        local_config_dir: Relative path to local config.ini-file.
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
        self.class_name = type(self).__name__

        self.section = section or self._default_section

        module = sys.modules[self.__class__.__module__]
        if isinstance(module, ModuleType):
            self.classpath = os.path.dirname(module.__file__)
        else:
            self.classpath = ""

        self.config = ConfigParser()

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
            logger_name=self.class_name,
            config=dict(self.config[self.section]),
        )

    def add_to_config(self, key, value):
        """Add values to config for the current section

        Args:
            key: Which key to add or update
            value: What value to give the key

        """
        self.config[self.section][key] = str(value)
