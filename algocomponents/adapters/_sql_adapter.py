import re
import uuid
from abc import abstractmethod
from typing import Dict, List

import pandas as pd

from algocomponents.config_reader import ConfigReader


class SQLAdapter(ConfigReader):
    """An abstract adapter used for connecting to a service and running queries.

    The purpose of the sql adapter is to generalize how we set up connections to
    different services. There will be one adapter per service.

    """

    default_max_rows_displayed = 20

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
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

    @abstractmethod
    def connect(self):
        """Connects the adapter.

        Non-abstract adapters extend this method using super().connect().

        """
        self.logger.info(f"{self.class_name} establishing connection...")

    @abstractmethod
    def is_connected(self) -> bool:
        """Checks whether the adapter is connected.

        Non-abstract adapters overwrite this method.

        Returns:
            True if the adapter is connected, False otherwise.

        """
        pass

    @abstractmethod
    def disconnect(self):
        """Checks whether the adapter is connected.

        Non-abstract adapters extend this method using super().disconnect().

        """
        self.logger.info(f"{self.class_name} disconnected.")

    @abstractmethod
    def table_exists(self, table: str) -> bool:
        """Checks whether a table exists.

        Non-abstract adapters overwrite this method.

        Args:
            table: The table to look for.

        """
        pass

    def get_table_columns(self, table: str) -> List[str]:
        """Gets the columns of a table.

        Adapters may overwrite this method if they have more efficient methods
        of doing this.

        Args:
            table: The table to look at.

        Returns:
            A list with the names of the columns.

        """
        df = self.run_sql_string(sql_string=f"SELECT * FROM {table} LIMIT 1")[0]
        # The .values part was added since converting an array to a list is way faster than doing it on an Index
        return df.columns.values.tolist()

    def table_contains_columns(
        self, table: str, columns: List[str], identical: bool = False
    ) -> bool:
        """Checks whether a table contains a list of columns.

        Adapters may overwrite this method if they have more efficient methods
        of doing this.

        Args:
            table: The table to look inside.
            columns: What columns to look for.
            identical: Whether the given columns should be identical to the table columns.

        Returns:
            True if the tables contains the columns, False otherwise

        """
        if len(columns) != len(set(columns)):
            raise ValueError(f"Columns contains duplicate values: {columns}")

        table_columns = self.get_table_columns(table=table)
        if identical:
            return sorted(table_columns) == sorted(columns)
        else:
            return set(columns).issubset(set(table_columns))

    def run_sql_file(
        self, path: str, format_variables: Dict[str, str] = None
    ) -> List[pd.DataFrame]:
        """Parses an SQL file and runs it using the run_sql_string-method().

        Args:
            path: Path to the SQL file, from project root.
            format_variables: A dictionary used to .format() the SQL string.

        Return:
            A list of pandas dataframes, where each pandas dataframe is the
            result of each semi colon separated query in the sql file.

        """
        with open(path, encoding="utf-8") as f:
            sql_string = f.read()
            return self.run_sql_string(
                sql_string=sql_string,
                format_variables=format_variables,
            )

    def run_sql_string(
        self, sql_string: str, format_variables: Dict[str, str] = None
    ) -> List[pd.DataFrame]:
        """Formats an SQL string and runs it using _format_table_names().

        Args:
            sql_string: The SQL string to run. Can be several queries ;-separated.
            format_variables: A dictionary used to .format() the SQL string.

        Return:
            A list of pandas dataframes, where each pandas dataframe is the
            result of each semi colon separated query in the sql file.

        """
        if sql_string.strip() == "":
            raise ValueError(f"attempted to run an empty query: {sql_string}")

        if not format_variables:
            format_variables = {}

        queries = sql_string.split(";")
        dataframes = []
        for query in queries:
            query = query.strip()

            if query == "":
                continue

            query = self.format_string(
                string=query, additional_format_variables=format_variables
            )
            query = self._format_table_names(query=query)
            self.logger.info("*****************************************")
            self.logger.info(f"Executing the following query: \n{query}")
            self.logger.info("*****************************************")
            df = self._run_formatted_query(query=query)

            dataframes.append(df)

        return dataframes

    @abstractmethod
    def _run_formatted_query(self, query: str) -> pd.DataFrame:
        """Runs an SQL query towards whichever service this adapter is connected.

        Non-abstract adapters overwrite this method.

        Args:
            query: The query to run.

        Returns:
            The result of the query as a pandas dataframe.

        """
        pass

    def _format_table_names(self, query: str, ignore_ctes: bool = True) -> str:
        """Run _format_table_name on all tables in a query.

        Uses the method find_table_names() to get all the tables in a query.

        Args:
            query: The string to format the table names in.
            ignore_ctes: Whether CTE:s should be ignored, defaults to True.

        Returns:
            The provided query, with table names formatted.

        """
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
    def _format_table_name(self, table: str) -> str:
        """Performs an adapter-specific formatting of the table.

        Non-abstract adapters overwrite this method.

        Args:
            table: The table to format.

        Returns:
            The table name, formatted to be adapter specific.

        """
        pass

    def find_possible_cte_names(self, sql: str) -> List[str]:
        """Uses regex to find possible CTE-names in a query.

        This method will always find all CTE:s, but in some queries it mistake
        things that are not CTE:s for CTE:s and return these as well. It will
        never return a table name.

        Args:
            sql: The query to find CTE:s in.

        Returns:
            A list of all possible cte names.

        """
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

    def find_table_names(self, sql: str, ignore_ctes: bool = True) -> List[str]:
        """Uses regex to find all table names in a query.

        Args:
            sql: The query to find tabla names in.
            ignore_ctes: Whether CTE:s should be ignored or not, defaults to True.

        Returns:
            A list of all table names in the sql.

        """
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

    def adapter_specific_filters(self, sql: str) -> str:
        """Filters to apply to a query when finding tables or CTE:s inside it.

        Adapters may overwrite this method if they have any filters to apply.

        Args:
            sql: The query an adapter may remove parts of.

        Returns:
            The sql ones said parts are removed.

        """
        return sql

    def remove_comments_from_sql(self, sql: str) -> str:
        """Remove comments from a query.

        Args:
            sql: The query to remove comments from.

        Returns:
            The sql without comments

        """
        lines = sql.split("\n")
        lines_without_comments = []
        for line in lines:
            line_before_comment = line.split("--")[0]
            lines_without_comments.append(line_before_comment)
        sql = "\n".join(lines_without_comments)
        return sql

    @abstractmethod
    def latest_query_as_pandas(self) -> pd.DataFrame:
        """Get the result of the latest query as a pandas dataframe.

        Non-abstract adapters overwrite this method.

        This method is intended for use in method cascading.

        Returns:
            The result of the latest query as a pandas dataframe.

        """
        pass

    def table_as_pandas_df(self, table: str) -> pd.DataFrame:
        """Return all rows in a table as a pandas dataframe.

        Adapters may overwrite this method if they have more efficient methods
        of converting a table into a pandas dataframe.

        Args:
            table: The table to return as a pandas dataframe.

        Returns:
            The table as a pandas dataframe.

        """
        return self.run_sql_string(f"SELECT * FROM {table}")[0]

    @abstractmethod
    def pandas_df_as_table(self, df: pd.DataFrame, table: str, overwrite: bool = False):
        """Creates a table and puts a pandas dataframe in it.

        Non-abstract adapters overwrite this method.

        Args:
            df: The pandas dataframe to put in a table.
            table: The table you want to create.
            overwrite: Whether to overwrite an existing table, defaults to False.

        """
        pass

    @abstractmethod
    def insert_pandas_df_into_table(self, df: pd.DataFrame, table: str):
        """Inserts a pandas dataframe into a table.

        Non-abstract adapters overwrite this method.

        Args:
            df: The pandas dataframe to insert into a table.
            table: The table where you want to insert it.

        """
        pass

    @abstractmethod
    def latest_query_as_csv(self, path: str):
        """Get the result of the latest query as a csv file.

        Non-abstract adapters overwrite this method.

        Args:
            path: The path to save the csv file to.

        """
        pass

    def table_is_empty(self, table: str) -> bool:
        """Checks whether a table is empty or not.

        Adapters may overwrite this method if they have more efficient methods
        of doing this.

        Args:
            table: The table to check if it is empty or not.

        Returns:
            True if the table exists, False otherwise.

        """
        return len(self.table_as_pandas_df(table)) == 0

    def count_rows_in_table(self, table: str) -> int:
        """Count the number of rows in a table.

        Adapters may overwrite this method if they have more efficient methods
        of doing this.

        Args:
            table: The table to count number of rows.

        Returns:
            The number of rows as a int.

        """
        df = self.run_sql_string(sql_string=f"SELECT * FROM {table}")[0]
        return len(df)
