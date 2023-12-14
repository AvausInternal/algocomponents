import pytest

from algocomponents.adapters import LocalSqliteAdapter
from algocomponents.adapters.custom_exceptions import (
    TableMissingException,
    ColumnMissingException,
)
from algocomponents.tasks import SQLPipeline, CheckSignificance


class EmptySQLPipeline(SQLPipeline):
    pass


class TestCheckSignificance:

    @classmethod
    def setup_class(cls):
        # create the testing database
        EmptySQLPipeline(
            sql_folder="check_significance_queries",
            sql_adapter=LocalSqliteAdapter(),
            sql_folder_relative_path=True,
        ).start()

    def test_successful_significance_check(self):
        checker = CheckSignificance(
            input_table="dummy_test_results",
            group_column="group_",
            kpi_columns=["sales"],
            sql_adapter=LocalSqliteAdapter(),
        )

        try:
            checker.start()
        except Exception as e:
            self.fail(f"Throws exception on setup: {e}")

    def test_missing_column(self):
        checker = CheckSignificance(
            input_table="dummy_test_results",
            group_column="group_",
            kpi_columns=["sales", "impressions"],
            sql_adapter=LocalSqliteAdapter(),
        )

        with pytest.raises(ColumnMissingException):
            checker.start()

    def test_missing_table(self):
        checker = CheckSignificance(
            input_table="missing_table",
            group_column="group_",
            kpi_columns=["sales"],
            sql_adapter=LocalSqliteAdapter(),
        )

        with pytest.raises(TableMissingException):
            checker.start()

    def test_too_many_groups(self):
        checker = CheckSignificance(
            input_table="dummy_test_results",
            group_column="group_",
            kpi_columns=["sales"],
            group_names=["test", "group", "additional_group"],
            sql_adapter=LocalSqliteAdapter(),
        )

        with pytest.raises(AssertionError):
            checker.start()
