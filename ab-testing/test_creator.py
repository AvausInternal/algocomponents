from google.cloud import bigquery
import pandas as pd
import yaml

from tools.tools import write_to_table, delete_from_table
from test_group_splitter import TestGroupSplitter


class TestCreator:

    def __init__(
            self,
            test_config_path
    ):
        # Load framework config parameters
        with open('settings/fw_config.yaml') as config:
            self.fw_params = yaml.safe_load(config)
        
        self.client = bigquery.Client(project=self.fw_params['PROJECT'])
        
        # Load test config parameters
        with open(test_config_path) as config:
            self.test_params = yaml.safe_load(config)
        

    def create_test(self, mode='add'):
        
        # Add test to tests table
        test_entry = pd.DataFrame(
            data={
                'test_name': [self.test_params['test_name']],
                'eligible_customers': [self.test_params['source_table']],
                'customer_key': [self.test_params['customer_key']],
                'start_date': [self.test_params.get('start_date', '')],
                'end_date': [self.test_params.get('end_date', '')],
            }
        )
        write_to_table(
            df=test_entry,
            client=self.client,
            project=self.fw_params['PROJECT'],
            dataset_name=self.fw_params['DATASET_NAME'],
            table_name="tests", 
            key='test_name', 
            key_value=self.test_params['test_name'], 
            mode=mode
        )

        # Add groups to groups table
        groups_entry = pd.DataFrame(
            data={
                'test_name': self.test_params['test_name'],
                'group_name': [g['name'] for g in self.test_params['groups']],
                'is_control': [g['is_control'] for g in self.test_params['groups']],
                'size': [g['size'] for g in self.test_params['groups']]
            }
        )
        write_to_table(
            df=groups_entry,
            client=self.client,
            project=self.fw_params['PROJECT'],
            dataset_name=self.fw_params['DATASET_NAME'],
            table_name="groups", 
            key='test_name', 
            key_value=self.test_params['test_name'], 
            mode=mode
        )

        # Add metrics to test_metrics table
        metric_entry = pd.DataFrame(
            data={
                'test_name': [self.test_params['test_name']],
                'metric_name': [self.test_params['metric_name']]
            }
        )
        write_to_table(
            df=metric_entry,
            client=self.client,
            project=self.fw_params['PROJECT'],
            dataset_name=self.fw_params['DATASET_NAME'],
            table_name="test_metrics", 
            key='test_name', 
            key_value=self.test_params['test_name'], 
            mode=mode
        )

        # Set the stratification columns
        try: 
            stratification_column_string = f"{', '.join([''] + self.test_params['stratify_by'] )}"
        except(KeyError):
            stratification_column_string = ""
        
        # Create pandas df to pass to splitter
        customer_df = self.client.query(
            """
                SELECT DISTINCT
                    {customer_key}
                    {strat_cols}
                FROM {source_table}
            """.format(
                customer_key=self.test_params['customer_key'], 
                source_table=self.test_params['source_table'],
                strat_cols=stratification_column_string
            )
        ).to_dataframe()
        customer_df[self.test_params['customer_key']] = customer_df[self.test_params['customer_key']].astype("string")

        # Instantiate test group splitter
        splitter = TestGroupSplitter(
            customer_df,
            self.test_params['customer_key'],
            fractions=tuple(g['size'] for g in self.test_params['groups']),
            group_names=tuple(g['name'] for g in self.test_params['groups']),
            strat_columns=self.test_params.get('stratify_by',[])
        )

        # Create test and control group segments
        segments = splitter.split()

        # Prepend test name info
        segments.insert(loc=0, column='test_name', value=self.test_params['test_name'])

        # Add group segments to customer_segments table
        write_to_table(
            df=segments,
            client=self.client,
            project=self.fw_params['PROJECT'],
            dataset_name=self.fw_params['DATASET_NAME'],
            table_name="customer_segments",
            key='test_name', 
            key_value=self.test_params['test_name'], 
            mode=mode
        )
        
        
    def delete_test(self):
        # Remove from tests table
        delete_from_table(
            client=self.client,
            project=self.fw_params['PROJECT'],
            dataset_name=self.fw_params['DATASET_NAME'],
            table_name="tests", 
            key='test_name', 
            key_value=self.test_params['test_name']
        )
        
        # Remove from groups table
        delete_from_table(
            client=self.client,
            project=self.fw_params['PROJECT'],
            dataset_name=self.fw_params['DATASET_NAME'],
            table_name="groups", 
            key='test_name', 
            key_value=self.test_params['test_name']
        )
        
        # Remove from test metrics table
        delete_from_table(
            client=self.client,
            project=self.fw_params['PROJECT'],
            dataset_name=self.fw_params['DATASET_NAME'],
            table_name="test_metrics", 
            key='test_name', 
            key_value=self.test_params['test_name']
        )

        # Remove from customer segments table
        delete_from_table(
            client=self.client,
            project=self.fw_params['PROJECT'],
            dataset_name=self.fw_params['DATASET_NAME'],
            table_name="customer_segments",
            key='test_name', 
            key_value=self.test_params['test_name']
        )
        
        # Remove from test results table
        delete_from_table(
            client=self.client,
            project=self.fw_params['PROJECT'],
            dataset_name=self.fw_params['DATASET_NAME'],
            table_name="test_results", 
            key='test_name', 
            key_value=self.test_params['test_name']
        )
