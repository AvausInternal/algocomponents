from abc import ABC, abstractmethod
from configparser import ConfigParser
from typing import Dict

from algocomponents.utils import LoggieDoggie
from definitions import GLOBAL_CONFIG


class SQLAdapter(LoggieDoggie, ABC):
    """An abstract adapter used for connecting to a service and running queries.

    SQLAdapter will by default read the global config file. If a config is
    given, the global config file will still be parsed but the supplied config
    will take precedence over the global config file.

    The purpose of the sql adapter is to generalize how we set up connections to
    different services. There will be one adapter per service.
    """

    def __init__(self, overriding_config: ConfigParser = None):
        super().__init__()
        self.config = ConfigParser()
        self.config.optionxform = str  # Preserve casing in config file
        self.config.read(GLOBAL_CONFIG)

        # Append or overwrite values from overriding_config to config
        if overriding_config:
            for section in overriding_config:
                if section not in self.config.keys():
                    self.config.add_section(section)
                for key, value in overriding_config[section].items():
                    self.config[section][key] = value

        class_name = type(self).__name__
        if class_name in self.config:
            self.adapter_format_variables = self.config[class_name]
        else:
            self.adapter_format_variables = self.config["DEFAULT"]

    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def check_connection(self):
        pass

    @abstractmethod
    def disconnect(self):
        pass

    @abstractmethod
    def run_sql(self, sql: str):
        pass

    def run_sql_file(self, path: str, format_variables: Dict[str, str]):
        with open(path) as f:
            sql = f.read()
            queries = sql.split(";")
            for query in queries:
                query = query.strip()
                if query:
                    format_variables.update(self.adapter_format_variables)
                    query = query.format(**format_variables)
                    self.run_sql(query)
