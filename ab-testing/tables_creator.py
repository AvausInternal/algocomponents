from google.cloud import bigquery
import yaml

class TableCreator:
    
    def __init__(self):
        # Read the config file for framework detail
        with open('settings/fw_config.yaml') as config:
            self.fw_params = yaml.safe_load(config)

        # Get BigQuery connection
        self.client = bigquery.Client()
        
        # Creating data set and tabels
        self.create_dateset()
        self.create_tables()
        
    def create_dateset(self):
        # Set up date set config
        dataset_id = "{PROJECT}.{DATASET}".format(PROJECT=self.client.project, DATASET=self.fw_params['DATASET_NAME'])
        dataset = bigquery.Dataset(dataset_id)
        dataset.location = self.fw_params['LOCATION']

        # Create Data set
        try:
            dataset = self.client.create_dataset(dataset, timeout=30)
            print("Created dataset {}.{}".format(self.client.project, dataset.dataset_id))
        except:
            pass
        
    def create_tables(self):
        # Create table schema
        table_schemas = {
            'customer_segments': [
                bigquery.SchemaField("test_name", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("group_name", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("customer_key", "STRING", mode="REQUIRED")
            ],
            'groups': [
                bigquery.SchemaField("test_name", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("group_name", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("is_control", "BOOLEAN", mode="REQUIRED"),
                bigquery.SchemaField("size", "FLOAT", mode="REQUIRED"),
            ],
            'metrics': [
                bigquery.SchemaField("metric_name", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("description", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("sql", "STRING", mode="REQUIRED")
            ],
            'test_metrics': [
                bigquery.SchemaField("test_name", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("metric_name", "STRING", mode="REQUIRED")
            ],
            'test_results': [
                bigquery.SchemaField("test_name", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("group_name", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("metric_mean", "FLOAT", mode="REQUIRED"),
                bigquery.SchemaField("metric_name", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("metric_std", "FLOAT", mode="REQUIRED"),
                bigquery.SchemaField("significance", "FLOAT", mode="REQUIRED")
            ],
            'tests': [
                bigquery.SchemaField("test_name", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("eligible_customers", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("customer_key", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("start_date", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("end_date", "STRING", mode="REQUIRED")
            ]
        }

        # Create Tables
        for table_name in table_schemas:
            table_id = "{PROJECT}.{DATASET}.{TABLE}".format(
                            PROJECT=self.client.project,
                            DATASET=self.fw_params['DATASET_NAME'],
                            TABLE=table_name
                            )
            table = bigquery.Table(table_id, schema=table_schemas[table_name])
            try:
                table = self.client.create_table(table)
                print(
                    "Created table {}.{}.{}".format(table.project, table.dataset_id, table.table_id)
                )
            except:
                pass
