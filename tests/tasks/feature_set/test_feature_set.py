import os
from unittest import TestCase

import pytest

from algocomponents.adapters import LocalSqliteAdapter
from algocomponents.adapters.custom_exceptions import (
    TableMissingException,
    DataMismatchException,
)
from algocomponents.tasks import FeatureBase, Feature, FeatureSet, SQLPipeline


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
    """A simple feature that..."""

    input_columns = [
        "user_id",
        "product_id",
    ]
    output_primary_keys = [
        "user_id",
    ]
    output_columns_created = [
        "n_products_bought",
    ]


# Define class here so finding sql folder is easier
class SimpleFeatureSet(FeatureSet):
    output_primary_keys = [
        "user_id",
        "product_id",
    ]
    output_columns_created = []


class TestFeatureBase(TestCase):

    sql_adapter = LocalSqliteAdapter()

    def test_base_case(self):
        global_config_path = os.path.join(
            "tests", "tasks", "feature_set", "feature_set_config"
        )
        base_table = "{TMP_DB}.feature_base_test"
        new_table = "{TMP_DB}.pre_existing_table"

        # Prepare 'prexisting' tables for example:
        # # todo: debug this by making it to a feature base to sovle the problem
        # prepare_example_tables = SQLPipeline(
        #     global_config_dir=global_config_path,
        #     sql_folder=os.path.join("preparation_queries"),
        #     sql_adapter=self.sql_adapter,
        # )

        # prepare_example_tables.start()

        prepare_example_tables = SimpleFeatureBase(
            global_config_dir=global_config_path,
            sql_folder=os.path.join("preparation_queries"),
            sql_adapter=self.sql_adapter,
            output_table=new_table,
        )
        prepare_example_tables.start()

        # Construct the input table with a FeatureBase
        feature_base = SimpleFeatureBase(
            global_config_dir=global_config_path,
            sql_folder=os.path.join("make_feature_base_queries"),
            sql_adapter=self.sql_adapter,
            output_table=base_table, 
        )
        feature_base.start()

        feature = SimpleFeatureOne(
            global_config_dir=global_config_path,
            sql_folder="simple_feature_one_queries",
            sql_adapter=self.sql_adapter,
            input_table=base_table,
            output_table="{TMP_DB}.feature_one_output",
        )
        feature.start()

        # feature_set = SimpleFeatureSet(
        #     global_config_dir=global_config_path,
        #     sql_folder=os.path.join("feature_set", "feature_base_test_queries"),
        #     sql_adapter=self.sql_adapter,
        #     output_table=base_table,
        # )
        # feature_set.start()

        # Adapter disconnects as nothing else uses it, so we connect again manually
        feature.sql_adapter.connect()
        prepare_example_tables.sql_adapter.connect()
        assert prepare_example_tables.sql_adapter.table_exists(
            "tmp.PRODUCT_TABLE"
        )  # todo: fix hardcode

        assert "INPUT_TABLE" in feature.config[feature.section]
        assert feature.sql_adapter.table_exists(feature.input_table)
        assert feature.sql_adapter.table_exists(feature.output_table)

        test_feature_cols = sorted(
            feature.output_primary_keys + feature.output_columns_created
        )
        assert (
            sorted(feature.sql_adapter.get_table_columns(feature.output_table))
            == test_feature_cols
        )

        # input_columns = feature.sql_adapter.get_table_columns(feature.input_table)
        # assert sorted(input_columns) == sorted(feature.input_columns)

        # output_columns = feature.sql_adapter.get_table_columns(feature.output_table)
        # assert sorted(output_columns) == sorted(
        #     feature.output_primary_keys + feature.output_columns_created
        # )

        feature.sql_adapter.disconnect()

    # def test_output_column_missing(self):
    #     global_config_path = os.path.join("tests", "tasks", "feature_base_config")
    #     base_table = "{TMP_DB}.feature_base_test"
    #     feature_base = SimpleFeatureBase(
    #         global_config_dir=global_config_path,
    #         sql_folder="feature_base_test_queries",
    #         sql_adapter=self.sql_adapter,
    #         output_table=base_table,
    #     )
    #     feature_base.start()

    #     feature = SimpleFeature(
    #         global_config_dir=global_config_path,
    #         sql_folder="feature_test_queries_missing_output_column",
    #         sql_adapter=self.sql_adapter,
    #         input_table=base_table,
    #         output_table="{TMP_DB}.feature_test",
    #     )

    #     with pytest.raises(DataMismatchException):
    #         feature.start()

    # def test_output_table_missing(self):
    #     global_config_path = os.path.join("tests", "tasks", "feature_base_config")
    #     base_table = "{TMP_DB}.feature_base_test"
    #     feature_base = SimpleFeatureBase(
    #         global_config_dir=global_config_path,
    #         sql_folder="feature_base_test_queries",
    #         sql_adapter=self.sql_adapter,
    #         output_table=base_table,
    #     )
    #     feature_base.start()

    #     feature = SimpleFeature(
    #         global_config_dir=global_config_path,
    #         sql_folder="feature_test_queries_missing_output_table",
    #         sql_adapter=self.sql_adapter,
    #         input_table=base_table,
    #         output_table="{TMP_DB}.feature_test",
    #     )

    #     with pytest.raises(TableMissingException):
    #         feature.start()

    # def test_input_column_missing(self):
    #     global_config_path = os.path.join("tests", "tasks", "feature_base_config")
    #     base_table = "{TMP_DB}.feature_base_test"

    #     feature_base = SimpleFeatureBase(
    #         global_config_dir=global_config_path,
    #         sql_folder="feature_base_missing_columns_queries",
    #         sql_adapter=self.sql_adapter,
    #         output_table=base_table,
    #     )

    #     # Exception is thrown after output table is created,
    #     # so Feature can still use the table for this test
    #     with pytest.raises(DataMismatchException):
    #         feature_base.start()

    #     feature = SimpleFeature(
    #         global_config_dir=global_config_path,
    #         sql_folder="feature_base_test_queries",
    #         sql_adapter=self.sql_adapter,
    #         input_table=base_table,
    #         output_table="{TMP_DB}.feature_test",
    #     )

    #     with pytest.raises(DataMismatchException):
    #         feature.start()

    # def test_input_table_missing(self):
    #     global_config_path = os.path.join("tests", "tasks", "feature_base_config")
    #     base_table = "{TMP_DB}.feature_base_test"

    #     feature_base = SimpleFeatureBase(
    #         global_config_dir=global_config_path,
    #         sql_folder="feature_base_no_output_table_queries",
    #         sql_adapter=self.sql_adapter,
    #         output_table=base_table,
    #     )

    #     with pytest.raises(TableMissingException):
    #         feature_base.start()

    #     feature = SimpleFeature(
    #         global_config_dir=global_config_path,
    #         sql_folder="feature_base_test_queries",
    #         sql_adapter=self.sql_adapter,
    #         input_table=base_table,
    #         output_table="{TMP_DB}.feature_test",
    #     )

    #     with pytest.raises(TableMissingException):
    #         feature.start()
