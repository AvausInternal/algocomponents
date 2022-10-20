import os

from algocomponents.adapters import BigQueryAdapter, SparkAdapter
from algocomponents.adapters.custom_exceptions import (
    TableMissingException,
    DataMismatchException,
)
from algocomponents.tasks import AdapterTask, Task


class VerifyOutput(Task):
    """A task to verify the output of another task

    This task takes another task and compares that task's output table to
    another table specified by user. Can be used to verify that task's output
    stays constant over time. Before using this task, you can save the task's
    output with SaveExpectedOutput task.

    Args:
        for_task: Which task we want to verify the output for
        task_output_table: The output table for the task
        expected_output_table: Where the expected output of the task is stored

    """

    def __init__(
        self,
        for_task: AdapterTask,
        task_output_table: str,
        expected_output_table: str,
        **kwargs,
    ):
        super().__init__(**kwargs)

        self.task = for_task
        self.expected_output_table = expected_output_table
        self.task_output_table = task_output_table
        self.sql_folder = os.path.join(self.classpath, "sql")

        # GCP and Spark supports only "EXCEPT DISTINCT" and sqlite support only "EXCEPT"
        if isinstance(self.task.sql_adapter, (BigQueryAdapter, SparkAdapter)):
            distinct_statement = "EXCEPT DISTINCT"
        else:
            distinct_statement = "EXCEPT"

        self.format_variables = {
            "DISTINCT_STATEMENT": distinct_statement,
            "EXPECTED_OUTPUT_TABLE": expected_output_table,
            "TASK_OUTPUT_TABLE": task_output_table,
        }

    def run(self):
        """Verifies the output of self.task

        This checks if the output table is exactly identical to the expected
        output table. Many parts of SQL are not deterministic, keep this in mind
        when verifying outputs.

        Raises:
            TableMissingException: If the output table does not exist, or if the
                expected output does not exist
            DataMismatchException: If the expected_output_table does not contain
                the same columns as the output_table, or if there are array
                columns in either table

        """
        sql_adapter = self.task.sql_adapter
        sql_adapter.connect()

        # check that the task's output table exists
        if not sql_adapter.table_exists(self.task_output_table):
            sql_adapter.disconnect()
            raise TableMissingException(
                f"Task's output table: {self.task_output_table} doesn't exist"
            )

        # check if table with the expected output exists
        if not sql_adapter.table_exists(self.expected_output_table):
            sql_adapter.disconnect()
            raise TableMissingException(
                f"Table {self.expected_output_table} doesn't exists. Save it first with SaveExpectedOutput class"
            )

        # check if the two tables have matching columns
        columns_expected_output_table = sorted(
            sql_adapter.get_table_columns(self.expected_output_table)
        )
        columns_task_output_table = sorted(
            sql_adapter.get_table_columns(self.task_output_table)
        )
        if columns_expected_output_table != columns_task_output_table:
            sql_adapter.disconnect()
            raise DataMismatchException(
                f"Tables don't match.\n"
                f"Columns in expected output table: {columns_expected_output_table}\n"
                f"Columns in task's output table: {columns_task_output_table}"
            )

        try:
            # run the sql query that compares two tables and returns mismatching rows
            result = sql_adapter.run_sql_file(
                os.path.join(self.sql_folder, "differences_in_two_table.sql"),
                self.format_variables,
            )
        # throws an error if tables had array columns
        except Exception as e:
            sql_adapter.disconnect()
            raise DataMismatchException(
                "Something went wrong. Possibly a table contains array columns, which is not supported",
                e,
            ) from None

        if len(result[0]) != 0:
            sql_adapter.disconnect()
            raise DataMismatchException("Tables are not identical")
        else:
            self.logger.info("Tables are identical")

        sql_adapter.disconnect()
