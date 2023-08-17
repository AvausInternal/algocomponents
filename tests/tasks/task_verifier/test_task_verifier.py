import os
import pytest

from algocomponents.adapters import LocalSqliteAdapter
from algocomponents.adapters.custom_exceptions import (
    DataMismatchException,
    TableMissingException,
)
from algocomponents.tasks import SQLPipeline
from algocomponents.tasks.task_verifier.save_expected_output import SaveExpectedOutput
from algocomponents.tasks.task_verifier.verify_output import VerifyOutput


class EmptySQLPipeline(SQLPipeline):
    pass


class TestTaskVerifier:
    sql_pipeline = EmptySQLPipeline(sql_adapter=LocalSqliteAdapter())

    @classmethod
    def setup_class(cls):
        # create the testing database
        SQLPipeline(
            sql_folder=os.path.join(
                "tests", "tasks", "task_verifier", "task_verifier_queries"
            ),
            sql_adapter=LocalSqliteAdapter(),
            sql_folder_relative_path=False,
        ).start()

    # Tests for setupping the TaskVerifier
    def test_successful_setup(self):
        verifier = SaveExpectedOutput(
            for_task=self.sql_pipeline,
            task_output_table="table_with_data",
            expected_output_table="exp_out_table",
        )
        try:
            verifier.start()
        except Exception as e:
            self.fail("Throws exception on setup", e)

    def test_setup_missing_output_table(self):
        verifier = SaveExpectedOutput(
            for_task=self.sql_pipeline,
            task_output_table="table_which_doesnt_exist",
            expected_output_table="exp_out_table",
        )
        with pytest.raises(TableMissingException):
            verifier.start()

    # Tests for verifying task
    def test_missing_expected_output_table(self):
        verifier = VerifyOutput(
            for_task=self.sql_pipeline,
            task_output_table="table_with_data",
            expected_output_table="table_which_doesnt_exist",
        )

        with pytest.raises(TableMissingException):
            verifier.start()

    def test_missing_task_output_table(self):
        verifier = VerifyOutput(
            for_task=self.sql_pipeline,
            task_output_table="table_which_doesnt_exist",
            expected_output_table="table_with_data",
        )
        with pytest.raises(TableMissingException):
            verifier.start()

    def test_matching_data(self):
        verifier = VerifyOutput(
            for_task=self.sql_pipeline,
            task_output_table="table_with_data",
            expected_output_table="exp_out_table",
        )
        try:
            verifier.start()
        except:
            self.fail(f"Throws exception even though data matches")

    # same columns but missing one row
    def test_missing_row(self):
        verifier = VerifyOutput(
            for_task=self.sql_pipeline,
            task_output_table="table_with_missing_row",
            expected_output_table="exp_out_table",
        )
        with pytest.raises(DataMismatchException):
            verifier.start()

    def test_missing_row_reversed(self):
        verifier = VerifyOutput(
            for_task=self.sql_pipeline,
            task_output_table="exp_out_table",
            expected_output_table="table_with_missing_row",
        )
        with pytest.raises(DataMismatchException):
            verifier.start()

    # same columns and same number of rows but single value is different
    def test_single_value_difference(self):
        verifier = VerifyOutput(
            for_task=self.sql_pipeline,
            task_output_table="table_with_diff_value",
            expected_output_table="exp_out_table",
        )
        with pytest.raises(DataMismatchException):
            verifier.start()

    def test_single_value_difference_reversed(self):
        verifier = VerifyOutput(
            for_task=self.sql_pipeline,
            task_output_table="exp_out_table",
            expected_output_table="table_with_diff_value",
        )
        with pytest.raises(DataMismatchException):
            verifier.start()

    # one of the tables is missing one colunns
    def test_different_columns(self):
        verifier = VerifyOutput(
            for_task=self.sql_pipeline,
            task_output_table="table_with_diff_cols",
            expected_output_table="exp_out_table",
        )
        with pytest.raises(DataMismatchException):
            verifier.start()

    def test_different_columns_reversed(self):
        verifier = VerifyOutput(
            for_task=self.sql_pipeline,
            task_output_table="exp_out_table",
            expected_output_table="table_with_diff_cols",
        )
        with pytest.raises(DataMismatchException):
            verifier.start()
