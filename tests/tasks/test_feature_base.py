import os
from unittest import TestCase

import pytest

from algocomponents.adapters import LocalSqliteAdapter
from algocomponents.adapters.custom_exceptions import (
    TableMissingException,
    DataMismatchException,
)
from algocomponents.tasks import FeatureBase


# Define class here so finding sql folder is easier
class SimpleFeatureBase(FeatureBase):
    output_primary_keys = [
        "user_id",
        "product_id",
    ]
    output_columns_created = []


class TestFeatureBase(TestCase):

    sql_adapter = LocalSqliteAdapter()

    def test_base_case(self):
        feature_base = SimpleFeatureBase(
            global_config_dir=os.path.join("tests", "tasks", "feature_base_config"),
            sql_folder="feature_base_test_queries",
            sql_adapter=self.sql_adapter,
            output_table="{TMP_DB}.feature_base_test",
        )
        feature_base.start()

        # Adapter disconnects as nothing else uses it, so we connect again manually
        feature_base.sql_adapter.connect()

        assert "OUTPUT_TABLE" in feature_base.config[feature_base.section]
        assert feature_base.sql_adapter.table_exists(feature_base.output_table)

        columns = feature_base.sql_adapter.get_table_columns(feature_base.output_table)
        assert sorted(columns) == sorted(
            feature_base.output_primary_keys + feature_base.output_columns_created
        )

        feature_base.sql_adapter.disconnect()

    def test_lacking_output_table(self):
        with pytest.raises(TableMissingException):
            feature_base = SimpleFeatureBase(
                global_config_dir=os.path.join("tests", "tasks", "feature_base_config"),
                sql_folder="feature_base_no_output_table_queries",
                sql_adapter=self.sql_adapter,
                output_table="{TMP_DB}.feature_base_test",
            )
            feature_base.start()

    def test_lacking_columns_in_output_table(self):
        with pytest.raises(DataMismatchException):
            feature_base = SimpleFeatureBase(
                global_config_dir=os.path.join("tests", "tasks", "feature_base_config"),
                sql_folder="feature_base_missing_columns_queries",
                sql_adapter=self.sql_adapter,
                output_table="{TMP_DB}.feature_base_test",
            )
            feature_base.start()
