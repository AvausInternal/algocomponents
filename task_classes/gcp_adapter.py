from configparser import ConfigParser
from google.cloud import bigquery

from task_classes.sql_adapter import SQLAdapter


class GCPAdapter(SQLAdapter):
    """Used to run queries on BigQuery.

    This adapter is intended for running queries on Google BigQuery.
    The script expects that the user is authenticated in the affected 
    gcp project using googles python client libraries and setup instructions. 
    """

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
