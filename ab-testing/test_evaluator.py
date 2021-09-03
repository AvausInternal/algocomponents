from google.cloud import bigquery
import pandas as pd
import yaml
from scipy import stats

from datetime import date

from tools.tools import write_to_table, delete_from_table


class TestEvaluator:

    def __init__(
            self,
            test_name
    ):
        # Load framework config parameters
        with open('settings/fw_config.yaml') as config:
            self.fw_params = yaml.safe_load(config)
        
        self.client = bigquery.Client(project=self.fw_params['PROJECT'])
        
        self.test_name = test_name

    def evaluate_test(self, mode='add', ignore_dates=False):
        # Fetch test parameters
        test_df = self.client.query(
            """
                SELECT
                    *
                FROM {PROJECT}.ab_test.tests
                WHERE test_name = '{test_name}'
            """.format(PROJECT=self.fw_params['PROJECT'], test_name=self.test_name)
        ).to_dataframe()
        customer_key = test_df['customer_key'][0]
        start_date = test_df['start_date'][0]
        end_date = test_df['end_date'][0]
        
        today = str(date.today())
        
        if (not ignore_dates) & (end_date != '') & (today <= end_date):
            print(f"'{self.test_name}' cannot be evaluated yet. It runs between {start_date} and {end_date}.")
            return
        
        # Fetch metric name and sql query
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
        metric_query = df['sql'][0].format(START_DATE=start_date, END_DATE=end_date)

        # Generate metric on customer level
        customer_metric = self.client.query(metric_query).to_dataframe()
        
        # Convert customer_key to string type
        customer_metric[customer_key] = customer_metric[customer_key].astype("string")

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
                                         on=customer_key, how='inner')

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

        write_to_table(
            df=test_results,
            client=self.client,
            project=self.fw_params['PROJECT'],
            table_name="test_results", 
            key='test_name', 
            key_value=self.test_name, 
            mode=mode
        )
