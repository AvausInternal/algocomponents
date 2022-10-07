import logging
import os
from typing import List
from unittest import TestCase

import pandas as pd

from algocomponents.adapters import SQLAdapter
from algocomponents.tasks import Task


class LogTestingTask(Task):
    """Defined so that old loggers are not used in this test"""


class CustomAdapter(SQLAdapter):
    """Defined so that old loggers are not used in this test"""

    def connect(self):
        pass

    def is_connected(self):
        pass

    def disconnect(self):
        pass

    def table_exists(self, table: str) -> bool:
        pass

    def get_table_columns(self, table: str) -> List[str]:
        pass

    def _run_formatted_query(self, query: str):
        pass

    def _format_table_name(self, table: str):
        pass

    def latest_query_as_pandas(self):
        pass

    def pandas_df_as_table(self, df: pd.DataFrame, table: str, overwrite: bool = False):
        pass

    def insert_pandas_df_into_table(self, df: pd.DataFrame, table: str):
        pass

    def latest_query_as_csv(self, path: str):
        pass


class TestThatLoggersReactToConfigCorrectly(TestCase):

    global_config_dir = os.path.join("tests", "adapters", "logging_test_config")

    def test_that_task_gets_correct_logger(self):
        # Remove handlers from root logger set by pytest
        # Handlers on the root logger are inherited by all loggers. Handlers are
        # used to identify whether a logger has been initiated or not, so if the
        # root logger has handlers, all loggers will appear as already initiated
        # and are not given the handlers specified in the config files.
        logging.getLogger().handlers = []

        task = LogTestingTask(
            global_config_dir=self.global_config_dir, section="DEFAULT"
        )
        assert task.logger.isEnabledFor(logging.INFO)
        # Assert the logger has a filehandler
        assert any(
            isinstance(handler, logging.FileHandler) for handler in task.logger.handlers
        )

    def test_that_task_changes_logger_behaviour_on_different_config(self):
        # Remove handlers from root logger set by pytest
        logging.getLogger().handlers = []

        task = LogTestingTask(
            global_config_dir=self.global_config_dir, section="SILENT"
        )
        assert not task.logger.isEnabledFor(logging.INFO)
        assert task.logger.isEnabledFor(logging.WARNING)
        # Assert the logger does not have a filehandler
        assert not any(
            isinstance(handler, logging.FileHandler) for handler in task.logger.handlers
        )

    def test_that_adapter_gets_correct_logger(self):
        # Remove handlers from root logger set by pytest
        # Handlers on the root logger are inherited by all loggers. Handlers are
        # used to identify whether a logger has been initiated or not, so if the
        # root logger has handlers, all loggers will appear as already initiated
        # and are not given the handlers specified in the config files.
        logging.getLogger().handlers = []

        adapter = CustomAdapter(
            global_config_dir=self.global_config_dir, section="DEFAULT"
        )
        assert adapter.logger.isEnabledFor(logging.INFO)
        # Assert the logger has a filehandler
        assert any(
            isinstance(handler, logging.FileHandler)
            for handler in adapter.logger.handlers
        )

    def test_that_adapter_changes_logger_behaviour_on_different_config(self):
        # Remove handlers from root logger set by pytest
        logging.getLogger().handlers = []

        adapter = CustomAdapter(
            global_config_dir=self.global_config_dir, section="SILENT"
        )
        assert not adapter.logger.isEnabledFor(logging.INFO)
        assert adapter.logger.isEnabledFor(logging.WARNING)
        # Assert the logger does not have a filehandler
        assert not any(
            isinstance(handler, logging.FileHandler)
            for handler in adapter.logger.handlers
        )
