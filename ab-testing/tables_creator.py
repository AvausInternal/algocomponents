def create_tables():
    import yaml
    with open('settings/fw_config.yaml') as config:
        fw_params = yaml.safe_load(config)

        from google.cloud import bigquery

    client = bigquery.Client()

    dataset_id = "{PROJECT}.{DATASET}".format(PROJECT=client.project, DATASET=fw_params['DATASET_NAME'])
    dataset = bigquery.Dataset(dataset_id)
    dataset.location = fw_params['LOCATION']
    
    try:
        dataset = client.create_dataset(dataset, timeout=30)
        print("Created dataset {}.{}".format(client.project, dataset.dataset_id))
    except:
        print("Cannot create data set {}.{} Already Exists".format(client.project, dataset.dataset_id))
        
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
            bigquery.SchemaField("customer_key", "FLOAT", mode="REQUIRED"),
            bigquery.SchemaField("start_date", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("end_date", "FLOAT", mode="REQUIRED")
        ]
    }

    for table_name in table_schemas:
        table_id = "{PROJECT}.{DATASET}.{TABLE}".format(
                        PROJECT=client.project,
                        DATASET=fw_params['DATASET_NAME'],
                        TABLE=table_name
                        )
        table = bigquery.Table(table_id, schema=table_schemas[table_name])
        try:
            table = client.create_table(table)
            print(
                "Created table {}.{}.{}".format(table.project, table.dataset_id, table.table_id)
            )
        except:
            print(
                "Cannot create table {}.{}.{} Already Exists".format(table.project, table.dataset_id, table.table_id)
            )
