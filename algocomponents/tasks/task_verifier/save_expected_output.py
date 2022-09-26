import os
from sqlite3 import OperationalError
from google.api_core.exceptions import BadRequest

from algocomponents.adapters import GCPAdapter, SparkAdapter
from algocomponents.tasks import AdapterTask, Task


class SaveExpectedOutput(Task):
    """A task to store the output of another task

    Task that takes another task and saves that task's output to a table
    specified by user. After the output is saved, you can use the
    VerifyOutput task to verify that task's output stays constant
    over time.
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
