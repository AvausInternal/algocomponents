from unittest import TestCase

import pytest

from algocomponents.adapters import LocalSqliteAdapter
from algocomponents.tasks import SQLPipeline


class EmptySQLPipeline(SQLPipeline):
    """Created here to fix sql folder path"""


class TestSqlPipeline(TestCase):
    def test_correct_file_formatting(self):
        pipeline = EmptySQLPipeline(
            sql_adapter=LocalSqliteAdapter(),
            sql_folder="good_sql",
        )
        result = pipeline.start()

        assert result is not None

    def test_bad_file_formatting(self):
        with pytest.raises(NameError):
            EmptySQLPipeline(
                sql_adapter=LocalSqliteAdapter(),
                sql_folder="bad_sql",
            )

    def test_non_sql_files(self):
        pipeline = EmptySQLPipeline(
            sql_adapter=LocalSqliteAdapter(),
            sql_folder="other_files_also",
        )

        result = pipeline.start()

        assert result is not None
