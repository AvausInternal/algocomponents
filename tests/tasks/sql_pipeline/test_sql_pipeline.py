from configparser import ConfigParser

import pytest

from algocomponents.adapters import LocalSqliteAdapter
from algocomponents.tasks import SQLPipeline


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

    def test_get_all_formatted_queries(self):
        config = ConfigParser()
        config.set(section="DEFAULT", option="var_one", value="one")
        config.set(section="DEFAULT", option="var_two", value="two")
        config.set(section="DEFAULT", option="var_three", value="three")
        pipeline = EmptySQLPipeline(
            config=config,
            sql_adapter=LocalSqliteAdapter(),
            sql_folder="templated_sql",
        )

        correct_queries = [
            "SELECT one",
            "SELECT two",
            "SELECT three",
        ]

        formatted_queries = pipeline.get_formatted_queries_from_task_list()

        for formatted_query, correct_query in zip(formatted_queries, correct_queries):
            assert formatted_query == correct_query
