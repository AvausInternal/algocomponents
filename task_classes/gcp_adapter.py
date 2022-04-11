import os
from configparser import ConfigParser

from google.cloud import bigquery
from google.oauth2 import service_account

from definitions import ROOT_DIR
from task_classes.sql_adapter import SQLAdapter


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
        self.credentials = None 
        self.key_path = os.path.join(ROOT_DIR, ".gcp_credentials.json")

    def connect(self):
        self.credentials = service_account.Credentials.from_service_account_file(self.key_path)
        self.client = bigquery.Client(credentials=self.credentials, project=self.credentials.project_id)

    def check_connection(self):
        self.logger.info(self.credentials)
        self.logger.info(self.client)

    def disconnect(self):
        self.client.close() 

    def run_sql(self, sql: str):
        sql = sql.strip()
        self.logger.info(f"Executing the following query: \n{sql}")

        query_job = self.client.query(sql)
        rows = query_job.result()  

        if rows: 
            self.logger.info("Result")
            for row in rows: 
                self.logger.info(list(row.items()))
