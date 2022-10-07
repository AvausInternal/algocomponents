import re
from configparser import ConfigParser
from typing import List

import pandas as pd

from algocomponents.adapters import SQLAdapter


class GCPAdapter(SQLAdapter):
    """Used to run queries on BigQuery.

    This adapter is intended for running queries on Google BigQuery.
    The script expects that the user is authenticated in the affected
    gcp project using googles python client libraries and setup instructions.
    """

    def __init__(
        self,
        config: ConfigParser = None,
        section: str = "DEFAULT",
    ):
        super().__init__(config=config, section=section)
        self.client = None
        self.connected = False
        self.query_job = None

    def connect(self):
        super().connect()
        # Import inside method to allow non GCP-users of algocomponents
        # to use library without having to install the google package
        global bigquery
        from google.cloud import bigquery

        self.client = bigquery.Client()

    def is_connected(self):
        return self.client is not None

    def disconnect(self):
        self.client.close()
        self.client = None
        super().disconnect()

    def _format_table_name(self, table: str):
        table = table.replace("`", "")

        if "gcp_project" not in list(self.adapter_format_variables):
            self.logger.info(
                "The GCPAdapter does not have a gcp_project, tables are not formatted"
            )
            return f"`{table}`"

        if len(table.split(".")) > 2:
            self.logger.info("Using the gcp project already present in the table name")
            return f"`{table}`"

        gcp_project = self.adapter_format_variables["gcp_project"]
        if table.startswith(gcp_project + "."):
            table = table[len(gcp_project) + 1 :]
        return f"`{gcp_project}.{table}`"

    def table_exists(self, table: str) -> bool:
        from google.api_core.exceptions import NotFound

        formatted_table = self._format_table_name(table).replace("`", "")
        try:
            self.client.get_table(formatted_table)
            return True
        except NotFound:
            return False

    def get_table_columns(self, table: str) -> List[str]:
        formatted_table = self._format_table_name(table).replace("`", "")
        schema = self.client.get_table(formatted_table).schema
        columns_names = [column.name for column in schema]
        return columns_names

    def _run_formatted_query(self, query: str):
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

    def adapter_specific_filters(self, sql: str):
        sql = self.remove_extract_method_calls_from_sql(sql=sql)
        sql = self.remove_unnest_method_calls_from_sql(sql=sql)
        sql = self.remove_ml_methods_from_sql(sql=sql)
        return sql

    def remove_extract_method_calls_from_sql(self, sql: str):
        # regex explanation
        match = re.findall(
            # First, at least 1 newline or whitespace
            r"\s+"
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

    def remove_unnest_method_calls_from_sql(self, sql: str):
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

    def remove_ml_methods_from_sql(self, sql: str):
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

    def latest_query_as_pandas(self):
        return self.query_job.to_dataframe()

    def pandas_df_as_table(self, df: pd.DataFrame, table: str, overwrite: bool = False):
        self.pandas_df_helper_method(df, table, "WRITE_TRUNCATE")

    def insert_pandas_df_into_table(self, df: pd.DataFrame, table: str):
        self.pandas_df_helper_method(df, table, "WRITE_APPEND")

    def pandas_df_helper_method(
        self, df: pd.DataFrame, table: str, write_disposition: str
    ):
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
        dataframe = self.latest_query_as_pandas()
        dataframe.to_csv(path)
