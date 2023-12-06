import re
from typing import List

import pandas as pd

from algocomponents.adapters import SQLAdapter
from algocomponents.adapters.custom_exceptions import (
    TableAlreadyExistsException,
    TableMissingException,
)
from algocomponents.utils import require_connection


class BigQueryAdapter(SQLAdapter):
    """Used to run queries on BigQuery.

    This adapter is intended for running queries on Google BigQuery.
    The script expects that the user is authenticated in the affected
    gcp project using googles python client libraries and setup instructions.

    """

    def __init__(
        self,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.client = None
        self.connected = False
        self.query_job = None

    def connect(self):
        """Connects the adapter.

        This method imports the bigquery dependencies: Therefore, bigquery is
        not a required the installation unless this adapter is used.

        The connection is stored in self.client.

        """
        super().connect()
        # Import inside method to allow non GCP-users of algocomponents
        # to use library without having to install the google package
        global bigquery
        from google.cloud import bigquery

        if "serv_acc_key_path" in self.config[self.section].keys():
            from google.oauth2 import service_account

            key_path = self.config[self.section]["serv_acc_key_path"]
            credentials = service_account.Credentials.from_service_account_file(
                key_path,
                scopes=["https://www.googleapis.com/auth/cloud-platform"],
            )
            self.client = bigquery.Client(credentials=credentials)
        else:
            self.client = bigquery.Client()

    def is_connected(self) -> bool:
        """Checks whether the adapter is connected.

        As long as there is a self.client, the adapter is considered connected.

        Returns:
            True if the adapter is connected, False otherwise.

        """
        return self.client is not None

    @require_connection
    def disconnect(self):
        """Disconnects the adapter.

        This is done by closing the connection and setting self.client to None.

        """
        self.client.close()
        self.client = None
        super().disconnect()

    def _format_table_name(self, table: str) -> str:
        """Performs an adapter-specific formatting of the table.

        Will make any table into the format `gcp-project.database.table`.

            - Backticks are always added
            - Prepends the gcp-project supplied through config (unless there
              already is a gcp-project in the table, or if there is no
              gcp-project in the config given)

        Args:
            table: The table to format.

        Returns:
            The provided query, with table names formatted.

        """
        table = table.replace("`", "")

        if "gcp_project" not in list(self.adapter_format_variables):
            self.logger.info(
                "The BigQueryAdapter does not have a gcp_project, tables are not formatted"
            )
            return f"`{table}`"

        if len(table.split(".")) > 2:
            self.logger.info("Using the gcp project already present in the table name")
            return f"`{table}`"

        gcp_project = self.adapter_format_variables["gcp_project"]
        return f"`{gcp_project}.{table}`"

    @require_connection
    def table_exists(self, table: str) -> bool:
        """Checks whether a table exists.

        Args:
            table: The table to look for.

        Returns:
            True if the table exists and False if it does not

        """
        from google.api_core.exceptions import NotFound

        formatted_table = self._format_table_name(table).replace("`", "")
        try:
            self.client.get_table(formatted_table)
            return True
        except NotFound:
            return False

    @require_connection
    def get_table_columns(self, table: str) -> List[str]:
        """Gets the columns of a table.

        Args:
            table: The table to look at.

        Returns:
            A list of the table columns

        """
        formatted_table = self._format_table_name(table).replace("`", "")
        schema = self.client.get_table(formatted_table).schema
        columns_names = [column.name for column in schema]
        return columns_names

    @require_connection
    def _run_formatted_query(self, query: str) -> pd.DataFrame:
        """Runs a query towards BigQuery.

        Args:
            query: The query to run.

        Returns:
            The result of the query as a pandas dataframe. An empty dataframe
            will be returned if the statement simply manipulates tables like
            CREATE:ing och DROP:ing tables.

        """
        self.query_job = self.client.query(query)
        self.logger.info(
            "This query will process {} bytes.".format(
                self.query_job.total_bytes_processed
            )
        )
        df = self.query_job.to_dataframe()

        self.logger.info("Result")
        self.logger.info(f"\n{df.head(self.max_rows_displayed)}")

        return df

    def adapter_specific_filters(self, sql: str) -> str:
        """Filters to apply to a query when finding tables or CTE:s inside it.

        This filter removes EXTRACT, UNNEST and ML-methods from the sql.

        Returns:
            The filtered sql.

        """
        sql = self.remove_extract_method_calls_from_sql(sql=sql)
        sql = self.remove_unnest_method_calls_from_sql(sql=sql)
        sql = self.remove_ml_methods_from_sql(sql=sql)
        return sql

    def remove_extract_method_calls_from_sql(self, sql: str) -> str:
        """Removes EXTRACT method-calls from the sql.

        Args:
            sql: The sql to remove from.

        Returns:
            The sql without EXTRACT method-calls.

        """
        # regex explanation
        match = re.findall(
            # First, at least 1 newline, whitespace or open parenthesis
            r"[\s(]+"
            # The extract keyword, followed by some or no whitespace characters
            r"(?:extract)\s*"
            # Everything from open paranthesis to close paranthesis
            r"\([^)]*\)",
            # Search in the sql string
            sql,
            # Ignore case
            re.IGNORECASE,
        )

        # replace every match with an empty string
        for x in match:
            sql = sql.replace(x, "")

        return sql

    def remove_unnest_method_calls_from_sql(self, sql: str) -> str:
        """Removes UNNEST method-calls from the sql.

        Args:
            sql: The sql to remove from.

        Returns:
            The sql without UNNEST method-calls.

        """
        # regex explanation
        match = re.findall(
            # First, at least 1 newline or whitespace
            r"\s+"
            # from or join, followed by 1 or more newline or whitespace
            # ?: is used to make it a non-capturing group. preventing re.findall
            # from only returning the match for the paranthesis
            r"(?:from|join)\s+"
            # The unnest keyword, followed by some or no whitespace characters
            r"(?:unnest)"
            # Everything from open paranthesis to close paranthesis
            r"\([^)]*\)",
            # Search in the sql string
            sql,
            # Ignore case
            re.IGNORECASE,
        )

        # replace every match with an empty string
        for x in match:
            sql = sql.replace(x, "")

        return sql

    def remove_ml_methods_from_sql(self, sql: str) -> str:
        """Removes ML method-calls from the sql.

        Args:
            sql: The sql to remove from.

        Returns:
            The sql without ML method-calls.

        """
        # regex explanation
        match = re.findall(
            # First, at least 1 newline or whitespace
            r"\s+"
            # Maybe FROM, if the ML-method is used that way
            r"(from\s+)?"
            # ml. followed by at least one word-character and maybe whitespace
            r"(?:ml.)\w+\s*"
            # Everything from open paranthesis to close paranthesis
            r"\([^)]*\)",
            # Search in the sql string
            sql,
            # Ignore case
            re.IGNORECASE,
        )

        # replace every match with an empty string
        for x in match:
            sql = sql.replace(x, "")

        return sql

    def latest_query_as_pandas(self) -> pd.DataFrame:
        """Get the result of the latest query as a pandas dataframe.

        Returns:
            A pandas dataframe of the latest query_job

        """
        return self.query_job.to_dataframe()

    @require_connection
    def pandas_df_as_table(self, df: pd.DataFrame, table: str, overwrite: bool = False):
        """Creates a table and puts a pandas dataframe in it.

        Args:
            df: The pandas dataframe to put in a table.
            table: The table you want to create.
            overwrite: Whether to overwrite an existing table, defaults to False.

        Raises:
            ValueError: If the dataframe does not have column names

        """
        if overwrite:
            self.pandas_df_helper_method(df, table, "WRITE_TRUNCATE")
        else:
            table = self._format_table_name(table=table)
            if self.table_exists(table):
                raise TableAlreadyExistsException(
                    f"Table {table} already exists. If you wish to overwrite it, call this method with overwrite=True"
                )
            self.pandas_df_helper_method(df, table, "WRITE_TRUNCATE")

    @require_connection
    def insert_pandas_df_into_table(self, df: pd.DataFrame, table: str):
        """Inserts a pandas dataframe into a table.

        If the table does not already exist, it will be created.

        Args:
            df: The pandas dataframe to insert into a table.
            table: The table where you want to insert it.

        Raises:
            ValueError: If the dataframe does not have column names

        """
        self.pandas_df_helper_method(df, table, "WRITE_APPEND")

    @require_connection
    def pandas_df_helper_method(
        self, df: pd.DataFrame, table: str, write_disposition: str
    ):
        """Helper method for pandas_df_as_table() and pandas_df_helper_method().

        Args:
            df: The pandas dataframe to insert into a table.
            table: The table where you want to insert it.
            write_disposition: BigQuery argument for handling existing tables.

        Raises:
            ValueError: If the dataframe does not have column names

        """
        job_config = bigquery.LoadJobConfig(write_disposition=write_disposition)
        table = self._format_table_name(table).replace("`", "")

        try:
            job = self.client.load_table_from_dataframe(
                df, table, job_config=job_config
            )
            job.result()

        except TypeError as e:
            raise ValueError("Your dataframe is missing column names") from e

    def latest_query_as_csv(self, path: str):
        """Get the result of the latest query as a csv file.

        Args:
            path: The path to save the csv file to.

        """
        dataframe = self.latest_query_as_pandas()
        dataframe.to_csv(path)

    @require_connection
    def count_rows_in_table(self, table: str) -> int:
        """Count the number of rows in a table.

        Args:
            table: The table to count number of rows.

        Returns:
            The number of rows as a int.

        """
        if not self.table_exists(table):
            raise TableMissingException(f"Table {table} does not exist.")
        else:
            return self.run_sql_string(f"SELECT count(*) as row_count FROM {table}")[0][
                "row_count"
            ].iloc[0]
