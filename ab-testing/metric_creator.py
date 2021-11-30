from google.cloud import bigquery
import pandas as pd
import yaml

from tools.tools import write_to_table, delete_from_table


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
        write_to_table(
            df=metric_entry,
            client=self.client,
            project=self.fw_params['PROJECT'],
            dataset_name=self.fw_params['DATASET_NAME'],
            table_name='metrics', 
            key='metric_name', 
            key_value=self.metric_name, 
            mode=mode
        )
        
        
    def delete_metric(self, mode='add'):
        
        # Remove from metrics table
        delete_from_table(
            client=self.client,
            project=self.fw_params['PROJECT'],
            dataset_name=self.fw_params['DATASET_NAME'],
            table_name='metrics', 
            key='metric_name', 
            key_value=self.metric_name
        )
