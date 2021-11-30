# README
1. git clone the repository into a notebook server or from where you want to run the framework: https://bitbucket.org/avauspl/algofactory/src/master/
2. Open settings/fw_config.yaml and edit the parameters PROJECT, DATASET_NAME, REGION to your project and desired dataset name.
3. Run the create_tables() function as examplified in the example notebook "test_creation_interface.ipynb". This will create the dataset with the necessary tables in it.
4. Create at least one metric that you can use to evaluate your tests with. Instructions for this is found in the "test_creation_interface.ipynb". This will populate the DATASET_NAME.metrics table with your specified metric.
5. Copy the "example_test_config.yaml" in the settings folder and fill in the specific parameters for your test. Save the config with a name for the test and make sure the file ending is .yaml. The config looks as follows:

> test_name: Test 5 # The name of the test (needs to be unique from other tests)<br>
> start_date: '2011-08-01' # When the test starts<br>
> end_date: '2011-08-31' # When the test ends<br>
> source_table: algo-factory-dev.instacart_tf.orders_unique # From what table to divide into groups<br>
> customer_key: order_id # On what column to divide on<br>
> metric_name: last order # The name of the metric to evaluate on (needs to be created in framework as in step 4)<br>
> stratify_by: # if you want to use stratified sampling, specify the columns to stratify on, else delete this parameter<br>
> - eval_set <br>
> - order_number <br>
> groups: # Here you specify the groups that you want to have<br>
> - name: A # Name of first group<br>
>   size: 0.5 # Size (as a fraction) of the group<br>
>   is_control: false # Whether or not this is a control group<br>
> - name: B <br>
>   size: 0.3 <br>
>   is_control: true <br>
> - name: C <br>
>   size: 0.2 <br>
>   is_control: false <br>

6. Create a test by running TestCreator(path_to_config_file).create_test(). See the example notebook for this. This will populate the DATASET_NAME.tests with your new test and DATASET_NAME.groups with the specified groups of your test. This function will also split the customers into the specified groups and save the split in DATASET_NAME.customer_segments table.
7. When the current date has passed the end_date of a test, one can evaluate it by running TestCreator("name of test").evaluate_test(). See the example notebook for this. You can also evaluate a test before the end_time has passed by adding the flag ignore_dates=True as follows: TestCreator("name of test").evaluate_test(ignore_dates=True)
8. Open the template report in data studio found here: https://datastudio.google.com/u/0/reporting/eec31cf1-2768-45b1-852b-86622f34eed1
9. Make a copy of the report. If this is the first time, you need to provide some basic info about your country, company name and preferences. Then when you press make a copy, select "new data source" and "create data source". Select "BigQuery" and then navigate to your PROJECT.DATASET_NAME.test_results table. Press "CONNECT", then "ADD TO REPORT", then finally "Copy Report".
10. Select the the test name that you want to visualize. The preset is to show all tests which does not really make sense.