import os

from algocomponents.adapters.custom_exceptions import (
    TableMissingException,
    DataMismatchException,
)
from algocomponents.adapters import GCPAdapter, SparkAdapter
from algocomponents.tasks import AdapterTask, Task


class VerifyOutput(Task):
    """A task to verify the output of another task

    Task that takes another task and compares that task's output
    table to an another table specified by user. Can be used
    to verify that task's output stays constant over time.
    Before using this task, you can save the task's output
    with SaveExpectedOutput task.
    """

    def __init__(
        self,
        for_task: AdapterTask,  # task which output will be saved
        task_output_table: str,  # table where the task normally saves it's output
        expected_output_table: str,  # table where the output will be saved with this task
        **kwargs,
    ):
        super().__init__(**kwargs)

        self.task = for_task
        self.expected_output_table = expected_output_table
        self.task_output_table = task_output_table
        self.sql_folder = os.path.join(self.classpath, "sql")

        # GCP and Spark supports only "EXCEPT DISTINCT" and sqlite support only "EXCEPT"
        if isinstance(self.task.sql_adapter, (GCPAdapter, SparkAdapter)):
            distinct_statement = "EXCEPT DISTINCT"
        else:
            distinct_statement = "EXCEPT"

        self.format_variables = {
            "DISTINCT_STATEMENT": distinct_statement,
            "EXPECTED_OUTPUT_TABLE": expected_output_table,
            "TASK_OUTPUT_TABLE": task_output_table,
        }

    def run(self):
        sql_adapter = self.task.sql_adapter
        sql_adapter.connect()

        # check that the task's output table exists
        if not sql_adapter.table_exists(self.task_output_table):
            sql_adapter.disconnect()
            raise TableMissingException(
                f"Task's Output table: {self.task_output_table} doesn't exists"
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
                f"Tables don't match.\nColumns in expected output table: {columns_expected_output_table}\nColumns in task's output table: {columns_task_output_table}"
            )

        try:
            # make sql query that compares tables and returns mismatching rows
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
            raise DataMismatchException("Tables don't match")
        else:
            self.logger.info("Tables match")

        sql_adapter.disconnect()
