import os
from unittest import TestCase

import pytest

from algocomponents.adapters import LocalSqliteAdapter
from algocomponents.tasks import Dataset, Feature, FeatureBase, SQLPipeline, SQLTask
from algocomponents.adapters.custom_exceptions import DataMismatchException

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


class SimpleFaultyFeature(Feature):
    """A simple feature with the primary keys that intentionally
    do not exist, for testing purposes."""

    input_columns = ["wrongly_named_product_id"]
    output_primary_keys = [
        "wrongly_named_product_id",
    ]
    output_columns_created = []


class _(TestCase):
    """Tests concerning the initialisation of the class without start() method calls"""

    # globals
    sql_adapter = LocalSqliteAdapter()
    global_config_path = os.path.join("tests", "tasks", "dataset", "dataset_config")
    work_dir_path = os.path.join("tests", "tasks", "dataset")

    # dataset = Dataset(
    #     output_table="{tmp_db}.test_output",
    #     features=[],
    #     # input_table=base_table,
    #     input_table="{tmp_db}.feature_base_test",
    #     feature_base=None,
    #     import_columns="full",
    #     where_clause=None,
    #     drop_intermediate=False,
    #     target_label=False,
    #     global_config_dir=self.global_config_path,
    #     sql_adapter=self.sql_adapter,
    # )
    # dataset.start()


class TestDatasetinit(TestCase):
    """Tests concerning the initialisation of the class without start() method calls"""

    def test_init_featurelist(self):
        # crash: feature list given wrong data type
        with pytest.raises(ValueError):
            Dataset(
                input_table="fake_input_table",
                output_table="fake_output_table",
                features=["wrong_feature_datatype"],
            )

    def test_init_double_inputs(self):
        # input and feature base are both given
        with pytest.raises(ValueError):
            Dataset(
                input_table="fake_input_table",
                feature_base="fake_input_featurebase",
                output_table="fake_output_table",
                features=[],
            )

    def test_init_no_inputs(self):
        # neither  featurebase or input are given
        with pytest.raises(ValueError):
            Dataset(
                output_table="fake_output_table",
                features=[],
            )

    def test_init_verify(self):
        # When both verify is true we need an sql adapter
        with pytest.raises(ValueError):
            Dataset(
                input_table="fake_input_table",
                output_table="fake_output_table",
                features=[],
                verify=True,
                sql_adapter=None,
            ).startup()


class TestDatasetFeaures(TestCase):
    """Tests concerning the features and feature miss-matches

    # todo:
    #! a dataset with featurebase and output, but no features leads to confusing output table checks.
    # if features have output_columns_created = [] code crashes?
    """

    # globals
    sql_adapter = LocalSqliteAdapter()
    base_table = "{tmp_db}.feature_base_test"

    global_config_path = os.path.join("tests", "tasks", "dataset", "dataset_config")
    work_dir_path = os.path.join("tests", "tasks", "dataset")

    feature_base = SimpleFeatureBase(
        global_config_dir=global_config_path,
        sql_folder=os.path.join("make_feature_base_queries"),
        sql_adapter=sql_adapter,  # needed if you run it seperately.
        output_table=base_table,
    )

    faulty_feature = SimpleFaultyFeature(
        global_config_dir=global_config_path,
        sql_folder="simple_feature_one_queries",
        sql_adapter=sql_adapter,
        input_table=base_table,
        output_table="{tmp_db}.feature_one_output",
    )

    def test_featurebase_pk_missing(self):
        # a feature primary key not in the featurebase primary key list
        with pytest.raises(DataMismatchException):
            dataset = Dataset(
                output_table="{tmp_db}.test_output",
                feature_base=self.feature_base,
                features=[self.faulty_feature],
                global_config_dir=self.global_config_path,
                sql_adapter=self.sql_adapter,
            )
            dataset.start()

    def test_feature_pk_missing(self):
        # primary key from features not found in input table
        pass


class TestDataset(TestCase):
    """a typical joining scenario with preexisting tables
    everything in here is a WIP
    """

    # globals
    sql_adapter = LocalSqliteAdapter()
    global_config_path = os.path.join("tests", "tasks", "dataset", "dataset_config")
    work_dir_path = os.path.join("tests", "tasks", "dataset")

    def test_prexisting_tables_exist(self):

        # Prepare 'prexisting' tables for example:
        prepare_example_tables = SQLPipeline(
            global_config_dir=self.global_config_path,
            sql_folder=os.path.join(self.work_dir_path, "preparation_queries"),
            sql_folder_relative_path=False,
            sql_adapter=self.sql_adapter,
        )
        prepare_example_tables.start()
        prepare_example_tables.sql_adapter.connect()

        name = prepare_example_tables.config[prepare_example_tables.section][
            "pre_existing_table"
        ]
        name = name.format(
            **prepare_example_tables.config[prepare_example_tables.section]
        )

        assert self.sql_adapter.table_exists(name)

    #     assert self.sql_adapter.table_exists("{pre_existing_table}")

    # Table names. Note: these exist in the config as well.
    base_table = "{tmp_db}.feature_base_test"
    pre_existing_table = "{tmp_db}.pre_existing_table"

    # Construct the input table with a FeatureBase.
    feature_base = SimpleFeatureBase(
        global_config_dir=global_config_path,
        sql_folder=os.path.join("make_feature_base_queries"),
        sql_adapter=sql_adapter,  # needed if you run it seperately.
        output_table=base_table,
    )
    # feature_base.start()

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
    # dataset.start()
