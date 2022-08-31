import os
import re
from abc import ABC, abstractmethod
from configparser import ConfigParser
from typing import Dict, List

from algocomponents.utils import LoggieDoggie


class SQLAdapter(ABC):
    """An abstract adapter used for connecting to a service and running queries.

    SQLAdapter will by default read the global config file. If a config is
    given, the global config file will still be parsed but the supplied config
    will take precedence over the global config file.

    The purpose of the sql adapter is to generalize how we set up connections to
    different services. There will be one adapter per service.
    """

    def __init__(
        self,
        config: ConfigParser = None,
        section: str = "DEFAULT",
    ):
        self.class_name = type(self).__name__

        self.section = section

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

        if self.class_name in self.config:
            self.adapter_format_variables = self.config[self.class_name]
        else:
            self.adapter_format_variables = self.config[self.section]

        # Set a logger for the task
        self.logger = LoggieDoggie().fetch_logger(
            logger_name=self.class_name,
            config=dict(self.config[self.section]),
        )

    @abstractmethod
    def connect(self):
        self.logger.info(f"{self.class_name} establishing connection...")

    @abstractmethod
    def is_connected(self):
        pass

    @abstractmethod
    def disconnect(self):
        self.logger.info(f"{self.class_name} disconnected.")

    @abstractmethod
    def table_exists(self, table: str) -> bool:
        pass

    @abstractmethod
    def get_table_columns(self, table: str) -> List[str]:
        pass

    def run_sql_file(self, path: str, format_variables: Dict[str, str]):
        with open(path) as f:
            sql_string = f.read()
            self.run_sql_string(
                sql_string=sql_string,
                format_variables=format_variables,
            )

    def run_sql_string(self, sql_string: str, format_variables: Dict[str, str] = None):
        if not format_variables:
            format_variables = {}

        queries = sql_string.split(";")
        for query in queries:
            query = query.strip()

            if not query:
                continue

            if not self.is_connected():
                self.connect()

            query = self._format_query(query=query, format_variables=format_variables)
            query = self._format_table_names(query=query)
            self.logger.info(f"Executing the following query: \n{query}")
            self._run_formatted_query(query=query)

    @abstractmethod
    def _run_formatted_query(self, query: str):
        pass

    def _format_query(
        self, query: str, format_variables: Dict[str, str], max_depth: int = 5
    ):
        # Format until no change is detected to allow nested templating:
        # {OUTPUT_TABLE} -> {TMP_DB}.output_table -> tmp.output_table
        format_variables.update(self.adapter_format_variables)
        previous_query = ""
        depth = 0
        while query != previous_query:
            previous_query = query
            query = query.format(**format_variables)
            depth += 1
            if depth > max_depth:
                raise RecursionError(
                    f"Reached max reformatting depth of {max_depth} with:\n"
                    f"query:\n{query}\n"
                    f"previous_query:\n{previous_query}"
                )
        return query

    def _format_table_names(self, query: str, ignore_ctes: bool = True):
        tables = self.find_table_names(sql=query, ignore_ctes=ignore_ctes)
        for table in tables:
            reformatted_table = self._format_table_name(table=table)
            query = query.replace(table, reformatted_table)
        return query

    @abstractmethod
    def _format_table_name(self, table: str):
        pass

    def find_cte_names(self, sql: str) -> List[str]:
        # Remove newlines from sql
        sql = sql.replace("\n", " ")
        # Transform multi-whitespaces into single whitespace
        sql = " ".join(sql.split())

        # Allow adapter specific filtering of query
        sql = self.adapter_specific_filters(sql=sql)

        # regex explanation
        match = re.findall(
            # First, any amount of newline or whitespace, including 0
            r"\s*"
            # with, followed by 1 or more newline or whitespace
            # ?: is used to make it a non-capturing group. preventing re.findall
            # from only returning the match for the paranthesis
            r"(?:with)\s+"
            # The cte, which can consist of words, .'s, `'s -'s and *'s
            r"[\w.`\-\*]+",
            # Search in the sql string
            sql,
            # Ignore case
            re.IGNORECASE,
        )
        if not match:
            return []

        # Split every element in the list by space and take the last element,
        # which will be the table name. set() is used to make list unique
        first_withs = list(set([x.split("\n")[-1].split(" ")[-1] for x in match]))

        # regex explanation
        # It is worth noting that this regex CAN pick up things that are not
        # ctes, but will never miss any ctes. This is the important part, as
        # no cte should be formatted as a table.
        match = re.findall(
            # First, any amount of newline or whitespace, including 0
            r"\s*"
            # End paranthesis, some or none whitespace, comma and then some or none whitespace
            r"\)\s*,\s*"
            # If the comma matches, the next word is the next CTE
            # This is the step where other things can technically
            # match, but no cte can be missed
            r"\w+",
            # Search in the sql string
            sql,
            # Ignore case
            re.IGNORECASE,
        )

        trailing_withs = list(set([x.split("\n")[-1].split(" ")[-1] for x in match]))

        return first_withs + trailing_withs

    def find_table_names(self, sql: str, ignore_ctes: bool = True):
        # Remove newlines from sql
        sql = sql.replace("\n", " ")
        # Transform multi-whitespaces into single whitespace
        sql = " ".join(sql.split())

        sql = self.adapter_specific_filters(sql=sql)

        # regex explanation
        match = re.findall(
            # First, at least 1 newline or whitespace
            r"\s+"
            # from, join or table, followed by 1 or more newline or whitespace
            # ?: is used to make it a non-capturing group. preventing re.findall
            # from only returning the match for the paranthesis
            r"(?:from|join|table)\s+"
            # Maybe if exists / if not exists, then maybe newline / whitespace
            r"(?:if exists|if not exists)*\s*"
            # The actual table, which can consist of words, .'s, `'s -'s and *'s
            r"[\w.`\-\*]+",
            # Search in the sql string
            sql,
            # Ignore case
            re.IGNORECASE,
        )
        if not match:
            return []

        # Split every element in the list by space and take the last element,
        # which will be the table name. set() is used to make list unique
        tables = list(set([x.split("\n")[-1].split(" ")[-1] for x in match]))

        if ignore_ctes:
            ctes = self.find_cte_names(sql)
            tables = [t for t in tables if t not in ctes]

        return tables

    def adapter_specific_filters(self, sql: str):
        return sql

    @abstractmethod
    def latest_query_as_pandas(self):
        pass

    @abstractmethod
    def latest_query_as_csv(self, path: str):
        pass
