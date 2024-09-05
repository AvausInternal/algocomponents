import os
import sys
from abc import ABC
from configparser import ConfigParser
from typing import Dict

from algocomponents.utils import LoggieDoggie, merge_configs


class ConfigReader(ABC):
    """A class used to read and manage configs.

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

        # This is needed because there must always be a section in order to use
        # a ConfigParser, but there must also be a distinction between
        # explicitly setting the section to "DEFAULT" and passing None.
        # section_is_set is used to determine if the section can be overwritten,
        # i.e. whether the ConfigReader has "Strong opinions" on its section.
        if section:
            self.section_is_set = True
            self.section = section
        else:
            self.section_is_set = False
            self.section = self._default_section

        module = sys.modules[self.__class__.__module__]
        if hasattr(module, "__file__"):
            self.classpath = os.path.dirname(module.__file__)
        else:
            self.classpath = ""

        self.config = ConfigParser()
        self.global_config_dir = global_config_dir
        self.local_config_dir = local_config_dir

        # First read global config
        self.config.read(os.path.join(global_config_dir, "config.ini"))

        # Then append or overwrite from the local config file
        self.config.read(os.path.join(self.classpath, local_config_dir, "config.ini"))

        # Then append or overwrite from a passed config
        if config is not None:
            self.config = merge_configs(
                merge_this=config, into_this=self.config, overwrite=True
            )

        # Raise ValueError if section is not in config
        self.verify_section_is_in_config(self.section)

        # Set a logger for the task
        # As soon as this __init__() finishes, Tasks and Adapters want to be
        # able to use self.logger as part of their own __init__(), so this has
        # to happen here.
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

    def verify_section_is_in_config(self, section):
        """Verifies that the section exists in the config for this class

        Raises:
            ValueError: If the section is not in the config
        """
        available_sections = self.config.sections() + [self._default_section]
        if section not in available_sections:
            raise ValueError(
                f"Section {section} not found in config. "
                f"These are the available sections: {available_sections}"
            )

    def update_logger(self):
        """Update the logger with new config settings.

        Currently, this is code duplication, because the fetch_logger() method
        itself handles returning the same logger if it is called with the same
        settings. However, having this as a separate piece of code is necessary,
        and it is likely that this will eventually not be code duplication as
        the use cases "Setting up logging" and "Updating logging" are different.

        """
        self.logger = LoggieDoggie().fetch_logger(
            logger_name=self.class_name,
            config=dict(self.config[self.section]),
        )

    def format_string(
        self,
        string: str,
        additional_format_variables: Dict[str, str] = None,
        max_depth: int = 5,
    ) -> str:
        """Recursively .format():s a string given a dict until it does not change.

        A max depth is used, as writing a more general approach to this method
        involves solving self-referencing problems in the format variables. For
        example, {"a": "{b}", "b": "{a}"} which will cause "{a}" to be formatted
        into "{b}", which will format into "{a}", etc. There are solutions, but
        the added code complexity was deemed to not be worth it.

        Args:
            string: The string to format.
            additional_format_variables: A dictionary used to .format() the SQL string.
            max_depth: Max number of times .format() will be done.

        Returns:
            The provided string, formatted.

        Raises:
            RecursionError: When .format():ing more than max_depth times and the
                string is still changing

        Examples:
            {output_table} -> {tmp_db}.output_table -> tmp.output_table

        """
        if not additional_format_variables:
            additional_format_variables = {}

        format_variables = dict(self.config[self.section]).copy()
        format_variables.update(additional_format_variables)

        previous_string = ""
        depth = 0
        while string != previous_string:
            previous_string = string
            string = string.format(**format_variables)
            depth += 1
            if depth > max_depth:
                raise RecursionError(
                    f"Reached max reformatting depth of {max_depth} with:\n"
                    f"string:\n{string}\n"
                    f"previous_string:\n{previous_string}"
                )
        return string
