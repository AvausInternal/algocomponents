from google.cloud import bigquery
import pandas as pd
import yaml

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
        self.dataset = bigquery.Dataset('{PROJECT}.ab_test'.format(PROJECT=self.fw_params['PROJECT']))
        
        # Load test config parameters
        with open(test_config_path) as config:
            self.test_params = yaml.safe_load(config)
        

    def create_test(self):
        
        # Add test to tests table
        test_entry = pd.DataFrame(
            data={
                'test_name': [self.test_params['test_name']],
                'eligible_customers': [self.test_params['source_table']],
                'customer_key': [self.test_params['customer_key']]
            }
        )
        self.write_to_table(test_entry, "tests", overwrite=True)

        # Add groups to groups table
        groups_entry = pd.DataFrame(
            data={
                'test_name': self.test_params['test_name'],
                'group_name': [g['name'] for g in self.test_params['groups']],
                'is_control': [g['is_control'] for g in self.test_params['groups']],
                'size': [g['size'] for g in self.test_params['groups']]
            }
        )
        self.write_to_table(groups_entry, "groups", overwrite=True)

        # Add metrics to test_metrics table
        metric_entry = pd.DataFrame(
            data={
                'test_name': [self.test_params['test_name']],
                'metric_name': [self.test_params['metric_name']]
            }
        )
        self.write_to_table(metric_entry, "test_metrics", overwrite=True)

        # Create pandas df to pass to splitter
        customer_df = self.client.query(
            """
                SELECT DISTINCT
                    {customer_key}
                FROM {source_table}
            """.format(
                customer_key=self.test_params['customer_key'], 
                source_table=self.test_params['source_table']
            )
        ).to_dataframe()

        # Instantiate test group splitter
        splitter = TestGroupSplitter(
            customer_df,
            self.test_params['customer_key'],
            fractions=tuple(g['size'] for g in self.test_params['groups']),
            group_names=tuple(g['name'] for g in self.test_params['groups']),
        )

        # Create test and control group segments
        segments = splitter.split()

        # Prepend test name info
        segments.insert(loc=0, column='test_name', value=self.test_params['test_name'])

        # Add group segments to customer_segments table
        self.write_to_table(segments, "customer_segments", overwrite=True)

            
    def write_to_table(self, df, table_name, overwrite=False):
        # Job config
        if overwrite:
            job_config = bigquery.LoadJobConfig(write_disposition="WRITE_TRUNCATE")
        else:
            job_config = bigquery.LoadJobConfig()
        job_config.autodetect = True
        table = self.dataset.table(table_name)
        job = self.client.load_table_from_dataframe(
            dataframe=df, destination=table, job_config=job_config
        )
        job.result()
