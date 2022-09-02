import os
from typing import List
from unittest import TestCase

import pytest

from algocomponents.adapters import LocalSqliteAdapter
from algocomponents.tasks import FeatureBase, Feature, SQLPipeline


# Define class here so finding sql folder is easier
class SimpleFeatureBase(FeatureBase):
    output_primary_keys = [
        "user_id",
        "product_id",
    ]
    output_columns_created = []


# Define class here so finding sql folder is easier
class SimpleFeature(Feature):
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


class TestFeatureBase(TestCase):

    sql_adapter = LocalSqliteAdapter()

    def test_base_case(self):
        global_config_path = os.path.join("tests", "feature_base_config")
        connecting_table = "{TMP_DB}.feature_base_test"
        feature_base = SimpleFeatureBase(
            global_config_dir=global_config_path,
            sql_folder="feature_base_test_queries",
            sql_adapter=self.sql_adapter,
            output_table=connecting_table,
        )
        feature_base.start()

        feature = SimpleFeature(
            global_config_dir=global_config_path,
            sql_folder="feature_test_queries",
            sql_adapter=self.sql_adapter,
            input_table=connecting_table,
            output_table="{TMP_DB}.feature_test",
        )
        feature.start()

        # Adapter disconnects as nothing else uses it, so we connect again manually
        feature.sql_adapter.connect()

        assert "INPUT_TABLE" in feature.config[feature.section]
        assert feature.sql_adapter.table_exists(feature.input_table)

        input_columns = feature.sql_adapter.get_table_columns(feature.input_table)
        assert sorted(input_columns) == sorted(feature.input_columns)

        output_columns = feature.sql_adapter.get_table_columns(feature.output_table)
        assert sorted(output_columns) == sorted(
            feature.output_primary_keys + feature.output_columns_created
        )

        feature.sql_adapter.disconnect()

    def test_output_column_missing(self):
        global_config_path = os.path.join("tests", "feature_base_config")
        connecting_table = "{TMP_DB}.feature_base_test"
        feature_base = SimpleFeatureBase(
            global_config_dir=global_config_path,
            sql_folder="feature_base_test_queries",
            sql_adapter=self.sql_adapter,
            output_table=connecting_table,
        )
        feature_base.start()

        feature = SimpleFeature(
            global_config_dir=global_config_path,
            sql_folder="feature_test_queries_missing_output_column",
            sql_adapter=self.sql_adapter,
            input_table=connecting_table,
            output_table="{TMP_DB}.feature_test",
        )

        with pytest.raises(Exception):
            feature.start()

    def test_output_table_missing(self):
        global_config_path = os.path.join("tests", "feature_base_config")
        connecting_table = "{TMP_DB}.feature_base_test"
        feature_base = SimpleFeatureBase(
            global_config_dir=global_config_path,
            sql_folder="feature_base_test_queries",
            sql_adapter=self.sql_adapter,
            output_table=connecting_table,
        )
        feature_base.start()

        feature = SimpleFeature(
            global_config_dir=global_config_path,
            sql_folder="feature_test_queries_missing_output_table",
            sql_adapter=self.sql_adapter,
            input_table=connecting_table,
            output_table="{TMP_DB}.feature_test",
        )

        with pytest.raises(Exception):
            feature.start()

    def test_input_column_missing(self):
        global_config_path = os.path.join("tests", "feature_base_config")
        connecting_table = "{TMP_DB}.feature_base_test"

        feature_base = SimpleFeatureBase(
            global_config_dir=global_config_path,
            sql_folder="feature_base_missing_columns_queries",
            sql_adapter=self.sql_adapter,
            output_table=connecting_table,
        )

        # Exception is thrown after output table is created,
        # so Feature can still use the table for this test
        with pytest.raises(Exception):
            feature_base.start()

        feature = SimpleFeature(
            global_config_dir=global_config_path,
            sql_folder="feature_base_test_queries",
            sql_adapter=self.sql_adapter,
            input_table=connecting_table,
            output_table="{TMP_DB}.feature_test",
        )

        with pytest.raises(Exception):
            feature.start()

    def test_input_table_missing(self):
        global_config_path = os.path.join("tests", "feature_base_config")
        connecting_table = "{TMP_DB}.feature_base_test"

        feature_base = SimpleFeatureBase(
            global_config_dir=global_config_path,
            sql_folder="feature_base_no_output_table_queries",
            sql_adapter=self.sql_adapter,
            output_table=connecting_table,
        )

        with pytest.raises(Exception):
            feature_base.start()

        feature = SimpleFeature(
            global_config_dir=global_config_path,
            sql_folder="feature_base_test_queries",
            sql_adapter=self.sql_adapter,
            input_table=connecting_table,
            output_table="{TMP_DB}.feature_test",
        )

        with pytest.raises(Exception):
            feature.start()
