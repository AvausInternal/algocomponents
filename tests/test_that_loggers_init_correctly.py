import logging
from unittest import TestCase
import os
import sys

# This is required for github actions to find the algocomponents imports

# sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from algocomponents.adapters import (
    SQLAdapter,
    LocalSqliteAdapter,
    GCPAdapter,
    SparkAdapter,
    DatabricksAdapter,
)
from algocomponents.tasks import Task, GroupTask, SQLTask, SQLPipeline, AdapterTask


class ThatThatLoggersInitCorrectly(TestCase):

    root_logger = logging.getLogger()

    # Tasks
    def test_that_task_gets_correct_logger(self):
        task = Task()
        self.verify_logger(task.logger)

    def test_that_adapter_task_gets_correct_logger(self):
        task = AdapterTask()
        self.verify_logger(task.logger)

    def test_that_group_task_gets_correct_logger(self):
        task = GroupTask()
        self.verify_logger(task.logger)

    def test_that_sql_task_gets_correct_logger(self):
        task = SQLTask("SELECT 1")
        self.verify_logger(task.logger)

    def test_that_sql_pipeline_gets_correct_logger(self):
        task = SQLPipeline()
        self.verify_logger(task.logger)

    # Adapters
    def test_that_local_sqlite_adapter_gets_correct_logger(self):
        adapter = LocalSqliteAdapter()
        self.verify_logger(adapter.logger)

    def test_that_gcp_adapter_gets_correct_logger(self):
        adapter = GCPAdapter()
        self.verify_logger(adapter.logger)

    def test_that_spark_adapter_gets_correct_logger(self):
        adapter = SparkAdapter()
        self.verify_logger(adapter.logger)

    def test_that_databricks_adapter_gets_correct_logger(self):
        adapter = DatabricksAdapter()
        self.verify_logger(adapter.logger)

    def verify_logger(self, logger):
        assert logger is not None
        assert logger is not self.root_logger
        assert logger.hasHandlers()
