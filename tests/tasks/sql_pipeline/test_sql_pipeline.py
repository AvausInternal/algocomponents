import pytest

from algocomponents.adapters import LocalSqliteAdapter
from algocomponents.tasks import SQLPipeline
from tempfile import TemporaryDirectory


class EmptySQLPipeline(SQLPipeline):
    """Created here to fix sql folder path"""


class TestSqlPipeline:
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

    def test_get_sql_tasks_fails_on_empty_folder(self):
        with TemporaryDirectory() as temp_dir:
            with pytest.raises(FileNotFoundError):
                EmptySQLPipeline(sql_folder=temp_dir)

    def test_get_sql_tasks_fails_on_nonexistent_folder(self):
        with pytest.raises(FileNotFoundError):
            EmptySQLPipeline(sql_folder="non_existent_folder")
