import sqlite3
from typing import List

import pandas as pd

from algocomponents.adapters import SQLAdapter
from algocomponents.adapters.custom_exceptions import TableAlreadyExistsException


class LocalSqliteAdapter(SQLAdapter):
    """Used to run queries locally.

    This adapter exists to be able to run queries locally for development
    purposes. Such as mocking a number of queries, testing out a pipeline
    structure, etc.

    Args:
        commit_queries: Whether tables created should remain once disconnected

    """

    db_file = "local_sqlite.db"

    def __init__(
        self,
        commit_queries: bool = True,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.commit_queries = commit_queries
        self.db_path = self.db_file
        self.connection = None
        self.cursor = None

    def connect(self):
        """Connects the adapter

        The connection is stored in self.cursor

        """
        super().connect()
        self.connection = sqlite3.connect(self.db_path)
        self.cursor = self.connection.cursor()
        self.logger.info(sqlite3.version)

    def is_connected(self):
        """Checks whether the adapter is connected

        Checks the existence and connection of self.cursor

        """
        if self.cursor is None:
            return False
        try:
            self.cursor.execute("SELECT 1")
            return True
        except sqlite3.ProgrammingError:
            return False

    def disconnect(self):
        """Disconnects the adapter

        This is done by closing the connections

        """
        self.connection.close()
        super().disconnect()

    def _format_table_name(self, table: str):
        """Performs an adapter-specific formatting of the table

        Removes backticks and replaces any .'s with _'s. This is to keep all
        local databases in one file for simplicity and for .gitignore

        """
        return table.replace("`", "").replace(".", "_")

    def table_exists(self, table: str) -> bool:
        """Checks whether a table exists

        Args:
            table: The table to look for

        """
        formatted_table = self._format_table_name(table)
        tables = self.cursor.execute(
            f"SELECT name FROM sqlite_master WHERE type='table' AND name='{formatted_table}'"
        ).fetchall()
        return len(tables) > 0

    def get_table_columns(self, table: str) -> List[str]:
        """Gets the columns of a table

        Args:
            table: The table to look at

        """
        formatted_table = self._format_table_name(table)
        description = self.cursor.execute(
            f"SELECT * FROM {formatted_table}"
        ).description
        columns_names = [column[0] for column in description]
        return columns_names

    def _run_formatted_query(self, query: str):
        """Runs a query towards SQLite

        The changes will persist if commit_queries was set to True when this
        adapter was created.

        Args:
            query: The query to run

        """
        query_job = self.cursor.execute(query)
        self.rows = self.cursor.fetchall()
        if query_job.description:
            self.columns = [column[0] for column in query_job.description]

        if self.rows:
            df = pd.DataFrame.from_records(
                data=self.rows,
                columns=self.columns,
            )
        else:
            df = pd.DataFrame()

        self.logger.info("Result")
        self.logger.info(f"\n{df.head(self.max_rows_displayed)}")

        if self.commit_queries:
            self.connection.commit()

        return df

    def latest_query_as_pandas(self):
        """Get the result of the latest query as a pandas dataframe"""
        return pd.DataFrame.from_records(
            data=self.rows,
            columns=self.columns,
        )

    def pandas_df_as_table(self, df: pd.DataFrame, table: str, overwrite: bool = False):
        """Creates a table and puts a pandas dataframe in it

        Args:
            df: The pandas dataframe to put in a table
            table: The table you want to create
            overwrite: Whether to overwrite an existing table, defaults to False

        """
        table = self._format_table_name(table=table)
        if overwrite:
            df.to_sql(table, self.connection, if_exists="replace", index=False)
        else:
            if self.table_exists(table):
                raise TableAlreadyExistsException(
                    f"Table {table} already exists. If you wish to overwrite it, call this method with overwrite=True"
                )
            df.to_sql(table, self.connection, index=False)

    def insert_pandas_df_into_table(self, df: pd.DataFrame, table: str):
        """Inserts a pandas dataframe into a table

        If the table does not already exist, it will be created

        Args:
            df: The pandas dataframe to insert into a table
            table: The table where you want to insert it

        """
        table = self._format_table_name(table=table)
        df.to_sql(table, self.connection, if_exists="append", index=False)

    def latest_query_as_csv(self, path: str):
        """Get the result of the latest query as a csv file

        Args:
            path: The path to save the csv file to.

        """
        dataframe = self.latest_query_as_pandas()
        dataframe.to_csv(path)
