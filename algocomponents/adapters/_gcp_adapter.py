from configparser import ConfigParser

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

    def _run_formatted_sql(self, sql: str):
        query_job = self.client.query(sql)
        rows = query_job.result()  

        if rows.total_rows != 0: 
            self.logger.info("Result")
            for row in rows: 
                self.logger.info(list(row.items()))
