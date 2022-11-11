.. Algocomponents documentation master file, created by
   sphinx-quickstart on Wed Oct 26 09:05:17 2022.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Algocomponents - Scalable python and SQL pipelines
==================================================

Algocomponents is a python package that makes it easy to build scalable python and SQL pipelines. It does this in 5 ways:

* Capture blocks of queries in classes and build reusable SQLPipelines.
* Connect to any type of database provider using Adapters.
* Put templated variables in queries to make them reusable.
* Organize Tasks and GroupTasks in task trees to build complex pipelines.
* Read, inherit and propagate global and local config files in your tasks and group tasks

Algocomponents consist of these five basic building blocks. With them, many other functionalities have been created that are also included. You can use these tools to build your own custom classes too!

.. code-block:: python

   # Run a query locally
   SQLTask(
      sql_string = "SELECT * FROM my_database.my_table",
      sql_adapter = LocalSqliteAdapter()
   ).start()

.. code-block:: python

   # Run a list of queries inside a folder
   SQLPipeline(
      sql_folder = "sql",
      sql_adapter = SparkAdapter()
   ).start()

.. code-block:: python

   # Run a series of SQLPipelines in order
   GroupTask(
      task_list = [
         my_first_sql_pipeline,
         my_second_sql_pipeline,
      ],
      sql_adapter = DatabricksAdapter(),
   ).start()

.. code-block:: python

   # Run a complex pipeline with custom tasks and customizable input
   GroupTask(
      task_list = [
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
      sql_adapter = BigQueryAdapter(),
   ).start()

.. toctree::
   :maxdepth: 5
   :caption: Contents:

   modules

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
