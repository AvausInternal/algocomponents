import os.path
from unittest import TestCase

import pandas as pd
import pytest

from algocomponents.adapters import LocalSqliteAdapter
from algocomponents.adapters.custom_exceptions import (
    DataMismatchException,
    TableIsEmptyException,
)
from algocomponents.tasks import SQLPipeline
from algocomponents.tasks.downsample_table.downsample_table import DownsampleTable
from algocomponents.tasks.stratify_groups.stratify_groups import StratifyGroups


class TestDownsampleTable(TestCase):
    sql_adapter = LocalSqliteAdapter(
        global_config_dir=os.path.join("tests", "tasks", "downsample_table", "config"),
    )
    downsample_input_table = "{tmp_db}.stratify_input_table"

    def create_input_table(self):
        pipeline = SQLPipeline(
            sql_adapter=self.sql_adapter,
            sql_folder=os.path.join("tests", "tasks", "downsample_table", "sql_setup"),
            sql_folder_relative_path=False,
            global_config_dir=os.path.join(
                "tests", "tasks", "downsample_table", "config"
            ),
        )
        pipeline.add_to_config("downsample_input_table", self.downsample_input_table)
        pipeline.start()

    def test_stratifying_with_correct_parameters(self):
        self.create_input_table()

        output_table = "{tmp_db}.stratified_output"
        downsample_ratio = 0.5
        DownsampleTable(
            input_table=self.downsample_input_table,
            output_table=output_table,
            downsample_ratio=downsample_ratio,
            stratify_on=["word"],
            sql_adapter=self.sql_adapter,
            global_config_dir=os.path.join(
                "tests", "tasks", "stratify_groups", "config"
            ),
        ).start()

        self.sql_adapter.connect()
        assert self.sql_adapter.table_exists(output_table)

        input_rows = self.sql_adapter.count_rows_in_table(self.downsample_input_table)
        output_rows = self.sql_adapter.count_rows_in_table(output_table)

        assert int(input_rows * downsample_ratio) == output_rows
        self.sql_adapter.disconnect()
