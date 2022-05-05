from configparser import ConfigParser
from typing import List

from algocomponents.adapters import SQLAdapter


class GCPAdapter(SQLAdapter):
    """Used to run queries on BigQuery.

    This adapter is intended for running queries on Google BigQuery.
    The script expects that the user is authenticated in the affected
    gcp project using googles python client libraries and setup instructions.
    """

    def __init__(self, config: ConfigParser = None):
        super().__init__(overriding_config=config)
        self.client = None
        self.connected = False
        self.query_job = None

    def connect(self):
        super().connect()
        # Import inside method to allow non GCP-users of algocomponents
        # to use library without having to install the google package
        from google.cloud import bigquery

        self.client = bigquery.Client()

    def is_connected(self):
        return self.client is not None

    def disconnect(self):
        self.client.close()
        self.client = None
        super().disconnect()

    def _format_table_name(self, table: str):
        assert "gcp_project" in list(self.adapter_format_variables), (
            "The GCPAdapter does not have a gcp_project set. It is either "
            "missing from the global config file, or it has not been "
            "supplied when instantiating the GCPAdapter"
        )

        table = table.replace("`", "")

        gcp_project = self.adapter_format_variables["gcp_project"]
        if table.startswith(gcp_project + "."):
            table = table[len(gcp_project) + 1 :]
        return f"`{gcp_project}.{table}`"

    def table_exists(self, table: str) -> bool:
        formatted_table = self._format_table_name(table).replace("`", "")
        try:
            self.client.get_table(formatted_table)
            return True
        except:
            return False

    def get_table_columns(self, table: str) -> List[str]:
        formatted_table = self._format_table_name(table).replace("`", "")
        schema = self.client.get_table(formatted_table).schema
        columns_names = [column.name for column in schema]
        return columns_names

    def _run_formatted_sql(self, sql: str):
        self.query_job = self.client.query(sql)
        self.logger.info(
            "This query will process {} bytes.".format(
                self.query_job.total_bytes_processed
            )
        )
        rows = self.query_job.result()

        if rows.total_rows != 0:
            self.logger.info("Result")
            for row in rows:
                self.logger.info(list(row.items()))

    def query_job_as_pandas(self):
        return self.query_job.to_dataframe()

    def query_job_as_csv(self, path: str):
        dataframe = self.query_job_as_pandas()
        dataframe.to_csv(path)
