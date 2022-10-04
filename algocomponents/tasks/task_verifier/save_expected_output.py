import os

from algocomponents.adapters.custom_exceptions import TableMissingException
from algocomponents.tasks import AdapterTask, Task


class SaveExpectedOutput(Task):
    """A task to store the output of another task

    This task takes another task and saves that task's output to a table
    specified by user. After the output is saved, you can use the VerifyOutput
    task to verify that the task's output stays constant over time.
    """

    def __init__(
        self,
        for_task: AdapterTask,  # task which output will be saved
        task_output_table: str,  # table where the task saves it's output
        expected_output_table: str,  # table where the expected output for this task will be saved
        **kwargs,
    ):
        super().__init__(**kwargs)

        self.task = for_task
        self.expected_output_table = expected_output_table
        self.task_output_table = task_output_table
        self.sql_folder = os.path.join(self.classpath, "sql")

        self.format_variables = {
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
                f"Output table: {self.task_output_table} doesn't exists"
            )

        # save the task's output to the location specified in the "expected_output_table"
        sql_adapter.run_sql_file(
            os.path.join(self.sql_folder, "save_expected_table.sql"),
            self.format_variables,
        )
        self.logger.info(
            f"Successfully saved the output table from {self.task_output_table} to {self.expected_output_table}"
        )

        sql_adapter.disconnect()
