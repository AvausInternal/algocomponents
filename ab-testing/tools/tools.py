from google.cloud import bigquery
import pandas as pd


def write_to_table(
    df,
    client,
    project,
    table_name,
    key, 
    key_value, 
    mode
):
    if mode == 'add':
        check = client.query(
        """
            SELECT
                {key}
            FROM {PROJECT}.ab_test.{table_name}
            WHERE {key} = '{key_value}'
        """.format(
            PROJECT=project,
            table_name=table_name,
            key=key,
            key_value=key_value
            )
        ).to_dataframe()
        if not check.empty:
            raise ValueError(f'{key} with the value \'{key_value}\' already exists.')
    elif mode == 'update':
        delete_from_table(table_name, key, key_value)
    else:
        raise ValueError("The mode parameter can have the values \'add\' or \'update\'.")

    dataset = bigquery.Dataset('{PROJECT}.ab_test'.format(PROJECT=project))
    
    # Job config
    job_config = bigquery.LoadJobConfig()
    job_config.autodetect = True
    table = dataset.table(table_name)
    job = client.load_table_from_dataframe(
        dataframe=df, destination=table, job_config=job_config
    )
    job.result()
    
    
def delete_from_table(
    client,
    project,
    table_name, 
    key, 
    key_value
):
    client.query(
    """
        DELETE FROM {PROJECT}.ab_test.{table_name}
        WHERE {key} = '{key_value}'
    """.format(
        PROJECT=project,
        table_name=table_name,
        key=key,
        key_value=key_value
        )
    )
