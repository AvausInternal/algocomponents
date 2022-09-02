import logging
import os
from unittest import TestCase

from algocomponents.tasks import Task


class LogTestingTask(Task):
    """Defined so that old loggers are not used in this test"""


class TestThatLoggersReactToConfigCorrectly(TestCase):

    global_config_dir = os.path.join("tests", "logging_test_config")

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

    def test_that_task_gets_correct_logger_2(self):
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
