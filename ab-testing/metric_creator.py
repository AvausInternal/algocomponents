from google.cloud import bigquery
import pandas as pd
import yaml


class MetricCreator:

    def __init__(
            self,
            metric_name: str,
            description: str,
            sql: str
    ):
        # Load framework config parameters
        with open('settings/fw_config.yaml') as config:
            self.fw_params = yaml.safe_load(config)
        
        self.client = bigquery.Client(project=self.fw_params['PROJECT'])
        self.dataset = bigquery.Dataset('{PROJECT}.ab_test'.format(PROJECT=self.fw_params['PROJECT']))
        
        self.metric_name = metric_name
        self.description = description
        self.sql = sql
        

    def create_metric(self, mode='add'):
        
        # Add test to tests table
        metric_entry = pd.DataFrame(
            data={
                'metric_name': [self.metric_name],
                'description': [self.description],
                'sql': [self.sql]
            }
        )
        self.write_to_table(
            metric_entry, 
            'metrics', 
            'metric_name', 
            self.metric_name, 
            mode
        )

            
    def write_to_table(self, df, table_name, key, key_value, mode):
        if mode == 'add':
            check = self.client.query(
            """
                SELECT
                    {key}
                FROM {PROJECT}.ab_test.{table_name}
                WHERE {key} = '{key_value}'
            """.format(
                PROJECT=self.fw_params['PROJECT'],
                table_name=table_name,
                key=key,
                key_value=key_value
                )
            ).to_dataframe()
            if not check.empty:
                raise ValueError(f'{key} with the value \'{key_value}\' already exists.')
        elif mode == 'update' or mode == 'delete':
            self.client.query(
            """
                DELETE FROM {PROJECT}.ab_test.{table_name}
                WHERE {key} = '{key_value}'
            """.format(
                PROJECT=self.fw_params['PROJECT'],
                table_name=table_name,
                key=key,
                key_value=key_value
                )
            )
            if mode == 'delete': return
        else:
            raise ValueError("The mode parameter can have the values \'add\', \'update\', or \'delete\'.")

        # Job config
        job_config = bigquery.LoadJobConfig()
        job_config.autodetect = True
        table = self.dataset.table(table_name)
        job = self.client.load_table_from_dataframe(
            dataframe=df, destination=table, job_config=job_config
        )
        job.result()