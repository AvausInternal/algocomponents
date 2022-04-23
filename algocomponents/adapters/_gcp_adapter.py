from configparser import ConfigParser

from google.cloud import bigquery

from algocomponents.adapters.sql_adapter import SQLAdapter


class GCPAdapter(SQLAdapter):
    """Used to run queries on BigQuery.

    This adapter is intended for running queries on Google BigQuery.
    The script expects a file named .credentials.json to exist in
    ROOT_DIR. It should contain a service account key with permissions:
    BigQuery Data Owner in dataset and BigQuery Job User in project.
    """

    default_max_rows = 20

    def __init__(self, config: ConfigParser = None):
        super().__init__(overriding_config=config)
        self.client = None 

    def connect(self):
        self.logger.info(f"GCPAdapter establishing connection...")
        self.client = bigquery.Client()

    def check_connection(self):
        self.logger.info(self.client)

    def disconnect(self):
        self.client.close()
        self.logger.info(f"GCPAdapter disconnected.")

    def run_sql(self, sql: str):
        sql = sql.strip()
        self.logger.info(f"Executing the following query: \n{sql}")

        query_job = self.client.query(sql)
        rows = query_job.result()  

        if rows: 
            self.logger.info("Result")
            for row in rows: 
                self.logger.info(list(row.items()))
