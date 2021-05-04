from google.cloud import bigquery
import pandas as pd
import yaml
from scipy import stats


class TestEvaluator:

    def __init__(
            self,
            test_name
    ):
        # Load framework config parameters
        with open('settings/fw_config.yaml') as config:
            self.fw_params = yaml.safe_load(config)
        
        self.client = bigquery.Client(project=self.fw_params['PROJECT'])
        self.dataset = bigquery.Dataset('{PROJECT}.ab_test'.format(PROJECT=self.fw_params['PROJECT']))
        
        self.test_name = test_name

    def evaluate_test(self, mode='add'):
        # Fetch metric sql query
        df = self.client.query(
            """
                SELECT
                    *
                FROM {PROJECT}.ab_test.test_metrics t
                INNER JOIN {PROJECT}.ab_test.metrics m
                    ON t.metric_name = m.metric_name
                WHERE t.test_name = '{test_name}'
            """.format(PROJECT=self.fw_params['PROJECT'], test_name=self.test_name)
        ).to_dataframe()
        metric_name = df['metric_name'][0]
        metric_query = df['sql'][0]

        # Generate metric on customer level
        customer_metric = self.client.query(metric_query).to_dataframe()
        
        # Fetch customer key for the test
        customer_key = self.client.query(
            """
                SELECT
                    *
                FROM {PROJECT}.ab_test.tests
                WHERE test_name = '{test_name}'
            """.format(PROJECT=self.fw_params['PROJECT'], test_name=self.test_name)
        ).to_dataframe()['customer_key'][0]

        # Fetch customer segments
        segments = self.client.query(
            """
                SELECT
                    group_name,
                    customer_key AS {customer_key}
                FROM {PROJECT}.ab_test.customer_segments
                WHERE test_name = '{test_name}'
            """.format(PROJECT=self.fw_params['PROJECT'], test_name=self.test_name, customer_key=customer_key)
        ).to_dataframe()

        # Join segment data to customer metrics table
        joined_df = customer_metric.join(segments.set_index(customer_key),
                                         on='{customer_key}'.format(customer_key=customer_key), how='inner')

        # Calculate mean and standard deviation of metric for the segments
        result_mean = joined_df.groupby('group_name')['metric'].mean()
        result_std = joined_df.groupby('group_name')['metric'].std()

        # Fetch groups data
        groups_df = self.client.query(
            """
                SELECT
                    group_name,
                    is_control
                FROM {PROJECT}.ab_test.groups
                WHERE test_name = '{test_name}'
            """.format(PROJECT=self.fw_params['PROJECT'], test_name=self.test_name)
        ).to_dataframe()
        
        pops = {}
        for g in groups_df['group_name']:
            pops[g] = list(joined_df.where(joined_df['group_name'] == g).dropna()['metric'])

        control = groups_df.where(groups_df['is_control']).dropna()['group_name'].values[0]

        test_results = pd.DataFrame()

        for g in groups_df['group_name']:
            t_score, p_value = stats.ttest_ind(pops[g], pops[control])
            data = {
                'group_name': g,
                'metric_name': metric_name,
                'metric_mean': result_mean[g],
                'metric_std': result_std[g],
                'significance': p_value
            }
            test_results = test_results.append(data, ignore_index=True)

        # Prepend test name info
        test_results.insert(loc=0, column='test_name', value=self.test_name)

        self.write_to_table(
            df=test_results, 
            table_name="test_results", 
            key='test_name', 
            key_value=self.test_name, 
            mode=mode
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
        elif mode == 'update':
            self.delete_from_table(table_name, key, key_value)
        else:
            raise ValueError("The mode parameter can have the values \'add\' or \'update\'.")

        # Job config
        job_config = bigquery.LoadJobConfig()
        job_config.autodetect = True
        table = self.dataset.table(table_name)
        job = self.client.load_table_from_dataframe(
            dataframe=df, destination=table, job_config=job_config
        )
        job.result()
        
    def delete_from_table(self, table_name, key, key_value):
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

