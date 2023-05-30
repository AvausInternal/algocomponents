import os
import pandas as pd
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
    """An example feature that uses the featurebase as an input to
    generate two features on the user level.
    """

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
    """A example feature that uses a prexisting table as input to
    add features on the product level.
    """

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


class IncorrectPrimaryKeyFeature(Feature):
    """A simple feature with the primary keys that intentionally
    do not exist elsewhere, for testing purposes."""

    input_columns = ["incorrectly_named_product_id"]
    output_primary_keys = [
        "incorrectly_named_product_id",
    ]
    output_columns_created = []


class TestDatasetinit(TestCase):
    """Tests concerning the initialisation of the class without start() method calls"""

    def test_init_featurelist(self):
        # feature list given wrong data type
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
        # neither featurebase or input are given
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


class TestDatasetFeatures(TestCase):
    """Tests concerning the features and feature miss-matches

    # todo:
        #! a dataset with featurebase and output, but no features leads to confusing output table checks.
        # if features have output_columns_created = [] code crashes?
        - full or selective choice
    """

    # globals
    sql_adapter = LocalSqliteAdapter()
    global_config_path = os.path.join("tests", "tasks", "dataset", "dataset_config")
    work_dir_path = os.path.join("tests", "tasks", "dataset")
    base_output_table = "{tmp_db}.feature_base_table"

    feature_base = SimpleFeatureBase(
        global_config_dir=global_config_path,
        sql_folder=os.path.join("make_feature_base_queries"),
        sql_adapter=sql_adapter,  # needed to run it seperately from Dataset
        output_table=base_output_table,
    )

    incorrect_primary_key_feature = IncorrectPrimaryKeyFeature(
        global_config_dir=global_config_path,
        sql_folder="simple_feature_one_queries",
        sql_adapter=sql_adapter,
        input_table=base_output_table,
        output_table="{tmp_db}.feature_one_output",
    )

    def test_featurebase_pk_missing(self):
        # a feature primary key not in the featurebase primary key list
        with pytest.raises(DataMismatchException):
            dataset = Dataset(
                output_table="{tmp_db}.test_output",
                feature_base=self.feature_base,
                features=[self.incorrect_primary_key_feature],
                global_config_dir=self.global_config_path,
                sql_adapter=self.sql_adapter,
            )
            dataset.start()

    def test_feature_pk_missing(self):
        # primary key from a feature is not found in input table

        self.feature_base.start()  # create input table
        with pytest.raises(DataMismatchException):
            dataset = Dataset(
                output_table="{tmp_db}.test_output",
                input_table=self.feature_base.output_table,
                features=[self.incorrect_primary_key_feature],
                global_config_dir=self.global_config_path,
                sql_adapter=self.sql_adapter,
            )
            dataset.start()


class TestDatasetOutcomes(TestCase):
    """A range of tests focusing on the output of the dataset

    #todo:
        - test drop intermediate
        - test total rows changed (throws DataMismatchException)
        - test column outputs wrong (should throw DataMismatchException)
        - test if it runs with and without verify


    """

    # globals
    sql_adapter = LocalSqliteAdapter()
    global_config_path = os.path.join("tests", "tasks", "dataset", "dataset_config")
    work_dir_path = os.path.join("tests", "tasks", "dataset")
    pre_existing_table = (
        "{tmp_db}.pre_existing_table"  # For clarity, but exists also in config
    )
    base_output_table = (
        "{tmp_db}.feature_base_table"  # For clarity, but exists also in config
    )

    # instantiate a simple feature
    feature_one = SimpleFeatureOne(
        global_config_dir=global_config_path,
        sql_folder="simple_feature_one_queries",
        input_table=base_output_table,
        output_table="{tmp_db}.feature_one_output",
    )

    # instantiate a simple feature
    feature_two = SimpleFeatureTwo(
        global_config_dir=global_config_path,
        sql_folder="simple_feature_two_queries",
        input_table=pre_existing_table,
        output_table="{tmp_db}.feature_two_output",
    )

    # instantiate feature with duplicate primary keys
    explosive_feature = SimpleFeatureOne(
        global_config_dir=global_config_path,
        sql_folder="simple_feature_one_queries",  # todo: make faulty query here
        input_table=base_output_table,
        output_table="{tmp_db}.feature_one_output",
    )

    def test_prexisting_tables_exist(self):
        # create and test 'prexisting' tables for our example scenario

        pre_existing_table = SQLPipeline(
            global_config_dir=self.global_config_path,
            sql_folder=os.path.join(self.work_dir_path, "preparation_queries"),
            sql_folder_relative_path=False,
            sql_adapter=self.sql_adapter,
        )
        pre_existing_table.start()
        pre_existing_table.sql_adapter.connect()

        name = pre_existing_table.config[pre_existing_table.section][
            "pre_existing_table"
        ]
        formatted_name = name.format(
            **pre_existing_table.config[pre_existing_table.section]
        )

        assert self.sql_adapter.table_exists(formatted_name)
        assert self.sql_adapter.count_rows_in_table(formatted_name) > 0
        assert set(self.sql_adapter.get_table_columns(formatted_name)) == set(
            ["product_id", "product_price", "product_weight"]
        )

    def test_for_explosive_join(self):
        # total rows must remain unchanged between input and output

        # with pytest.raises(DataMismatchException):
        # pass

        dataset = Dataset(
            output_table="{tmp_db}.test_output",
            features=[
                self.feature_one,
                self.feature_two,
            ],
            # input_table=base_output_table,
            input_table="{tmp_db}.feature_base_table",
            feature_base=None,  # feature_base,
            import_columns="full",
            where_clause=None,
            drop_intermediate=False,
            target_label=False,
            global_config_dir=self.global_config_path,
            sql_adapter=self.sql_adapter,
        )

        dataset.start()
