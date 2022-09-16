import os
from sqlite3 import OperationalError
from google.api_core.exceptions import BadRequest

from algocomponents.adapters import GCPAdapter, SparkAdapter
from algocomponents.tasks import AdapterTask, Task


class VerifyOutput(Task):
    """Task that can verify the output of another task"""

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
        if isinstance(self.task.sql_adapter, (GCPAdapter, SparkAdapter)):
            distinct_statement = "EXCEPT DISTINCT"
        else:
            distinct_statement = "EXCEPT"

        self.format_variables = {
            "DISTINCT_STATEMENT": distinct_statement,
            "EXPECTED_OUTPUT_TABLE": expected_output_table,
            "TASK_OUTPUT_TABLE": task_output_table,
        }

    def start(self):
        self.task.start()
        sql_adapter = self.task.sql_adapter
        sql_adapter.connect()

        # check that the task's output table exists
        if not sql_adapter.table_exists(self.task_output_table):
            sql_adapter.disconnect()
            raise Exception(
                f"Task's Output table: {self.task_output_table} doesn't exists"
            )

        # check if table with the expected output exists
        if not sql_adapter.table_exists(self.expected_output_table):
            sql_adapter.disconnect()
            raise Exception(
                f"You must run the setup first, table {self.expected_output_table} doesn't exists"
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
            raise Exception(
                f"Tables doesn't match.\nColumns in expected output table: {columns_expected_output_table}\nColumns in task's output table: {columns_task_output_table}"
            )

        try:
            # make sql query that compares tables and returns mismatching rows
            result = sql_adapter.run_sql_file(
                os.path.join(self.sql_folder, "differences_in_two_table.sql"),
                self.format_variables,
            )
        # throws an error if tables had array columns
        except (BadRequest, OperationalError) as e:
            sql_adapter.disconnect()
            raise Exception(
                "Tables contain array columns which are not supported",
                e,
            ) from None

        if len(result[0]) != 0:
            sql_adapter.disconnect()
            raise Exception("Tables doesn't match")
        else:
            self.logger.info("Tables match")

        sql_adapter.disconnect()


class SaveExpectedOutput(Task):
    """Task that can store the output of another task"""

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
        if isinstance(self.task.sql_adapter, (GCPAdapter, SparkAdapter)):
            distinct_statement = "EXCEPT DISTINCT"
        else:
            distinct_statement = "EXCEPT"
        self.format_variables = {
            "DISTINCT_STATEMENT": distinct_statement,
            "EXPECTED_OUTPUT_TABLE": expected_output_table,
            "TASK_OUTPUT_TABLE": task_output_table,
        }

    def start(self):
        self.task.start()
        sql_adapter = self.task.sql_adapter
        sql_adapter.connect()

        # check that the task's output table exists
        if not sql_adapter.table_exists(self.task_output_table):
            sql_adapter.disconnect()
            raise Exception(f"Output table: {self.task_output_table} doesn't exists")

        # save the task's output to the location specified in the "expected_output_table"
        sql_adapter.run_sql_file(
            os.path.join(self.sql_folder, "save_expected_table.sql"),
            self.format_variables,
        )
        self.logger.info(
            f"Succesfully ran the setup to the output table from {self.task_output_table} to {self.expected_output_table}"
        )

        sql_adapter.disconnect()
