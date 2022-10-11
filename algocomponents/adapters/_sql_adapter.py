import os
import re
import uuid
from abc import ABC, abstractmethod
from configparser import ConfigParser
from typing import Dict, List

import pandas as pd

from algocomponents.utils import LoggieDoggie, merge_configs


class SQLAdapter(ABC):
    """An abstract adapter used for connecting to a service and running queries.

    SQLAdapter will by default read the global config file. If a config is
    given, the global config file will still be parsed but the supplied config
    will take precedence over the global config file.

    The purpose of the sql adapter is to generalize how we set up connections to
    different services. There will be one adapter per service.
    """

    default_max_rows_displayed = 20

    def __init__(
        self,
        global_config_dir: str = "config",
        config: ConfigParser = None,
        section: str = "DEFAULT",
    ):
        self.class_name = type(self).__name__

        self.section = section

        self.config = ConfigParser()
        self.config.optionxform = str  # Preserve casing in config file

        # First read global config
        self.config.read(os.path.join(global_config_dir, "config.ini"))

        # Then append or overwrite from config inheritance
        if config is not None:
            self.config = merge_configs(
                merge_this=config, into_this=self.config, overwrite=True
            )

        if self.class_name in self.config:
            self.adapter_format_variables = self.config[self.class_name]
        else:
            self.adapter_format_variables = self.config[self.section]

        if "max_rows_displayed" in self.config[self.section]:
            self.max_rows_displayed = int(
                self.config[self.section]["max_rows_displayed"]
            )
        else:
            self.max_rows_displayed = self.default_max_rows_displayed

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

    def run_sql_file(
        self, path: str, format_variables: Dict[str, str] = None
    ) -> List[pd.DataFrame]:
        with open(path) as f:
            sql_string = f.read()
            return self.run_sql_string(
                sql_string=sql_string,
                format_variables=format_variables,
            )

    def run_sql_string(
        self, sql_string: str, format_variables: Dict[str, str] = None
    ) -> List[pd.DataFrame]:
        if not format_variables:
            format_variables = {}

        queries = sql_string.split(";")
        dataframes = []
        for query in queries:
            query = query.strip()

            if not query:
                continue

            if not self.is_connected():
                self.connect()

            query = self._format_query(query=query, format_variables=format_variables)
            query = self._format_table_names(query=query)
            self.logger.info(f"Executing the following query: \n{query}")

            df = self._run_formatted_query(query=query)

            dataframes.append(df)

        return dataframes

    @abstractmethod
    def _run_formatted_query(self, query: str) -> pd.DataFrame:
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
        # There is a trick here to prevent replacing a table which exists inside
        # another table, for example:

        #             customer_db.customers
        # downsampled_customer_db.customers_formatted

        # The replacement is done in a two step process. First, tables are
        # replaced with a unique identifier, then that unique identifier is
        # replaced with the formatted table.

        # For a string to exist inside another one, it must be shorter. So, we
        # order the list of tables so that it starts with the longest table,
        # and because the middle step of swapping the table for a unique
        # identifier exists, we will never accidentally format part of a table.
        tables.sort(key=len, reverse=True)
        unique_ids = {}

        # 1. downsampled_customer_db.customers_formatted -> 8q73456
        # 2. customer_db.customers -> 57he6gtf
        for table in tables:
            unique_ids[table] = str(uuid.uuid4())
            query = query.replace(table, unique_ids[table])

        # 3. 8q73456 -> formatted(downsampled_customer_db.customers_formatted)
        # 4. 57he6gtf -> formatted(customer_db.customers)
        for table in tables:
            reformatted_table = self._format_table_name(table=table)
            query = query.replace(unique_ids[table], reformatted_table)

        return query

    @abstractmethod
    def _format_table_name(self, table: str):
        pass

    def find_possible_cte_names(self, sql: str) -> List[str]:
        sql = self.remove_comments_from_sql(sql)
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
            # The cte, which can consist of words, .'s, `'s and -'s
            r"[\w.`-]+",
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
        sql = self.remove_comments_from_sql(sql)
        # Remove newlines from sql
        sql = sql.replace("\n", " ")
        # Transform multi-whitespaces into single whitespace
        sql = " ".join(sql.split())

        sql = self.adapter_specific_filters(sql=sql)

        # regex explanation
        match = re.findall(
            # First, any amount of newline or whitespace, including 0
            r"\s*"
            # set of different keywords followed by 1 or more newline or whitespace
            # ?: is used to make it a non-capturing group. preventing re.findall
            # from only returning the match for the paranthesis
            r"(?:from|join|table|insert|update|upsert|merge|delete|like|copy|clone|view|function|using)\s+"
            # Maybe if exists / if not exists / into, then maybe newline / whitespace
            r"(?:if exists|if not exists|into)*\s*"
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
            ctes = self.find_possible_cte_names(sql)
            tables = [t for t in tables if t not in ctes]

        return tables

    def adapter_specific_filters(self, sql: str):
        return sql

    def remove_comments_from_sql(self, sql: str):
        lines = sql.split("\n")
        lines_without_comments = []
        for line in lines:
            line_before_comment = line.split("--")[0]
            lines_without_comments.append(line_before_comment)
        sql = "\n".join(lines_without_comments)
        return sql

    @abstractmethod
    def latest_query_as_pandas(self):
        pass

    def table_as_pandas_df(self, table: str) -> pd.DataFrame:
        return self.run_sql_string(f"SELECT * FROM {table}")[0]

    @abstractmethod
    def pandas_df_as_table(self, df: pd.DataFrame, table: str, overwrite: bool = False):
        pass

    @abstractmethod
    def insert_pandas_df_into_table(self, df: pd.DataFrame, table: str):
        pass

    @abstractmethod
    def latest_query_as_csv(self, path: str):
        pass

    def table_is_empty(self, table: str) -> bool:
        return len(self.table_as_pandas_df(table)) == 0
