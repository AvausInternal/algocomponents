import os

from algocomponents.adapters import LocalSqliteAdapter
from algocomponents.tasks import Feature, FeatureBase, Dataset, SQLPipeline, SQLTask

# Define class here so finding sql folder is easier
class SimpleFeatureBase(FeatureBase):
    output_primary_keys = [
        "user_id",
        "product_id",
    ]
    output_columns_created = []


# Define class here so finding sql folder is easier
class SimpleFeatureOne(Feature):
    """A simple feature that uses our feature base as input"""

    input_columns = [
        "user_id",
        "product_id",
    ]
    output_primary_keys = [
        "user_id",
    ]
    output_columns_created = [
        "n_products_bought",
        "n_distinct_products_bought",
    ]


class SimpleFeatureTwo(Feature):
    """A simple feature that uses a prexisting table as input"""

    input_columns = [
        "product_id",
        "product_price",
        "product_weight",
    ]
    output_primary_keys = [
        "product_id",
    ]
    output_columns_created = [
        "price_per_kg",
        "product_price",
        "product_weight",
    ]


sql_adapter = LocalSqliteAdapter()

# global paths
# tests/tasks/dataset/feature_set_config/config.ini
global_config_path = os.path.join("tests", "tasks", "dataset", "dataset_config")
work_dir_path = os.path.join("tests", "tasks", "dataset")

# Table names. Note: these exist in the config as well.
base_table = "{tmp_db}.feature_base_test"
pre_existing_table = "{tmp_db}.pre_existing_table"

# Prepare 'prexisting' tables for example:
prepare_example_tables = SQLPipeline(
    global_config_dir=global_config_path,
    sql_folder=os.path.join(work_dir_path, "preparation_queries"),
    sql_folder_relative_path=False,
    sql_adapter=sql_adapter,
)
prepare_example_tables.sql_adapter.add_to_config(
    "pre_existing_table", "pre_existing_table"
)
# prepare_example_tables.start()

# Construct the input table with a FeatureBase.
feature_base = SimpleFeatureBase(
    global_config_dir=global_config_path,
    sql_folder=os.path.join("make_feature_base_queries"),
    sql_adapter=sql_adapter,  # needed if you run it seperately.
    output_table=base_table,
)
feature_base.start()

feature_one = SimpleFeatureOne(
    global_config_dir=global_config_path,
    sql_folder="simple_feature_one_queries",
    # sql_adapter=sql_adapter,
    input_table=base_table,
    output_table="{tmp_db}.feature_one_output",
)
# feature_one.start()

feature_two = SimpleFeatureTwo(
    global_config_dir=global_config_path,
    sql_folder="simple_feature_two_queries",
    # sql_adapter=sql_adapter,
    input_table=pre_existing_table,
    output_table="{tmp_db}.feature_two_output",
)
# feature_two.start()

dataset = Dataset(
    output_table="{tmp_db}.test_output",
    features=[
        feature_one,
        feature_two,
    ],
    # input_table=base_table,
    input_table="{tmp_db}.feature_base_test",
    feature_base=None,  # feature_base,
    import_columns="full",
    where_clause=None,
    drop_intermediate=False,
    target_label=False,
    global_config_dir=global_config_path,
    sql_adapter=sql_adapter,
)
dataset.start()
# featurebase has to actually run before we can use its output table '
# featurebase runs => we get a table => we can form the query.

# test for featurebase table:
# dataset.sql_adapter.connect()
# print("Exists: ==", dataset.sql_adapter.table_exists("tmp_feature_base_test"))
# assert dataset.sql_adapter.table_exists("tmp_feature_base_test")
# assert not dataset.sql_adapter.table_exists("tmp_feature_base_test")


# # * code to test your queries.
# task_runner = SQLTask(
#     sql_adapter=sql_adapter,
#     sql_string="SELECT * FROM tmp.feature_one_output",
#     global_config_dir=global_config_path,
# )
# # print(task_runner.run())
# task_runner = SQLTask(
#     sql_adapter=sql_adapter,
#     sql_string="SELECT * FROM tmp.feature_two_output",
#     global_config_dir=global_config_path,
# )
# # print(task_runner.run())
# task_runner = SQLTask(
#     sql_adapter=sql_adapter,
#     sql_string="SELECT * FROM tmp.feature_base_test",
#     global_config_dir=global_config_path,
# )
# print(task_runner.run())


# task_runner = SQLTask(
#     sql_adapter=sql_adapter,
#     sql_string=f"DROP TABLE {base_table}",
#     global_config_dir=global_config_path,
# )
# print(task_runner.run())

# task_runner = SQLTask(
#     sql_adapter=sql_adapter,
#     sql_string="SELECT * FROM {tmp_db}.test_output --debugging query",
#     global_config_dir=global_config_path,
# )
# print(task_runner.run())


# print(task_runner.run())
