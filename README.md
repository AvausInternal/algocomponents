# Algocomponents

**The Agent-Friendly ML Pipeline Structuring Tool**

Algocomponents is a python package that makes it easy to build scalable python and SQL pipelines. Because there's no UI and all pipeline structure remains directly in your repository as code, it is extremely easy for AI agents to write, use, and maintain complex data workflows.

It builds scalable pipelines in 5 ways:

* Capture blocks of queries in classes and build reusable SQLPipelines.
* Connect to any type of database provider using Adapters.
* Put templated variables in queries to make them reusable.
* Organize Tasks and GroupTasks in task trees to build complex pipelines.
* Read, inherit and propagate global and local config files in your tasks and group tasks

Algocomponents consist of these five basic building blocks. With them, many other functionalities have been created that are also included. You can use these tools to build your own custom classes too!

## Documentation
Full documentation is available at [algocomponents.avaus.com](https://algocomponents.avaus.com).

## Examples

### Run a query locally
```python
SQLTask(
    sql_string="SELECT * FROM my_database.my_table",
    sql_adapter=LocalSqliteAdapter()
).start()
```

### Run a list of queries inside a folder
```python
SQLPipeline(
    sql_folder="sql",
    sql_adapter=SparkAdapter()
).start()
```

### Run a series of SQLPipelines in order
```python
GroupTask(
    task_list=[
        my_first_sql_pipeline,
        my_second_sql_pipeline,
    ],
    sql_adapter=DatabricksAdapter(),
).start()
```

### Run a complex pipeline with custom tasks and customizable input
```python
GroupTask(
    task_list=[
        DataCleaning(
            timestamp=datetime.now(),
            output_table_path="{analytics_db}.clean_data",
        ),
        CreateFeatureSet(
            months_of_data=6,
            replace_null_with_zero=True,
            input_table_path="{analytics_db}.clean_data",
            output_table_path="{analytics_db}.feature_set",
        ),
    ],
    sql_adapter=BigQueryAdapter(),
).start()
```

## Contributing
Please refer to [CONTRIBUTING.md](CONTRIBUTING.md) for information on how to contribute to this project.

## Code of Conduct
Please read and follow our [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

## License
This project is licensed under the [GNU General Public License v3.0](LICENSE).
