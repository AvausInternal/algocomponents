import os
import re
from abc import ABC, abstractmethod
from configparser import ConfigParser
from typing import Dict, List

from algocomponents.utils import LoggieDoggie


class SQLAdapter(LoggieDoggie, ABC):
    """An abstract adapter used for connecting to a service and running queries.

    SQLAdapter will by default read the global config file. If a config is
    given, the global config file will still be parsed but the supplied config
    will take precedence over the global config file.

    The purpose of the sql adapter is to generalize how we set up connections to
    different services. There will be one adapter per service.
    """

    def __init__(
            self,
            overriding_config: ConfigParser = None
    ):
        super().__init__()
        self.config = ConfigParser()
        self.config.optionxform = str  # Preserve casing in config file
        self.config.read(os.path.join("config", "config.ini"))

        # Append or overwrite values from overriding_config to config
        if overriding_config:
            for section in overriding_config:
                if section not in self.config.keys():
                    self.config.add_section(section)
                for key, value in overriding_config[section].items():
                    self.config[section][key] = value

        self.class_name = type(self).__name__
        if self.class_name in self.config:
            self.adapter_format_variables = self.config[self.class_name]
        else:
            self.adapter_format_variables = self.config["DEFAULT"]

    @abstractmethod
    def connect(self):
        self.logger.info(f"{self.class_name} establishing connection...")

    @abstractmethod
    def is_connected(self):
        pass

    @abstractmethod
    def disconnect(self):
        self.logger.info(f"{self.class_name} disconnected.")

    def run_sql_file(self, path: str, format_variables: Dict[str, str]):
        with open(path) as f:
            sql_string = f.read()
            self.run_sql_string(
                sql_string=sql_string,
                format_variables=format_variables
            )

    def run_sql_string(self, sql_string: str, format_variables: Dict[str, str]):
        queries = sql_string.split(";")
        for query in queries:
            query = query.strip()
            if query:
                format_variables.update(self.adapter_format_variables)
                query = query.format(**format_variables)
                query = self.format_table_names(query=query)
                self.run_sql(query)

    def run_sql(self, sql: str):
        if not self.is_connected():
            self.connect()

        sql = sql.strip()
        self.logger.info(f"Executing the following query: \n{sql}")

        self._run_formatted_sql(sql=sql)

    @abstractmethod
    def _run_formatted_sql(self, sql: str):
        pass

    def format_table_names(self, query: str, ignore_ctes: bool = True):
        query = query.replace("`", "")
        tables = self.find_table_names(sql=query, ignore_ctes=ignore_ctes)
        for table in tables:
            reformatted_table = self._format_table_name(table=table)
            query = query.replace(table, reformatted_table)
        return query

    @abstractmethod
    def _format_table_name(self, table: str):
        pass

    def find_cte_names(self, sql: str) -> List[str]:
        # Use ?: in a group to make it a non-capturing group, preventing
        # re.findall from only returning the match for the paranthesis
        match = re.findall(r"\s+(?:with)\s+[\w.-]+", sql.lower())
        if not match:
            return []

        # Split every element in the list by space and take the last element,
        # which will be the table name. set() is used to make list unique
        return list(set(map(lambda x: x.split("\n")[-1].split(" ")[-1], match)))

    def find_table_names(self, sql: str, ignore_ctes: bool = True):
        # Use ?: in a group to make it a non-capturing group, preventing
        # re.findall from only returning the match for the paranthesis
        match = re.findall(r"\s+(?:from|join|table)\s+[\w.-]+", sql.lower())
        if not match:
            return []

        # Split every element in the list by space and take the last element,
        # which will be the table name. set() is used to make list unique
        tables = list(set(map(lambda x: x.split("\n")[-1].split(" ")[-1], match)))

        if ignore_ctes:
            ctes = self.find_cte_names(sql)
            tables = [t for t in tables if t not in ctes]

        return tables
