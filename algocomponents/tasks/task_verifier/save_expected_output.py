import os

from algocomponents.adapters.custom_exceptions import TableMissingException
from algocomponents.tasks import Task


class SaveExpectedOutput(Task):
    """A task to store the output of another task.

    This task takes another task and saves that task's output to a table
    specified by user. After the output is saved, you can use the VerifyOutput
    task to verify that the task's output stays constant over time.

    Args:
        for_task: Which task we want to save the expected output for.
        task_output_table: The output table for the task.
        expected_output_table: Where we want to save the expected output.

    """

    def __init__(
        self,
        for_task: Task,
        task_output_table: str,
        expected_output_table: str,
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
        """Saves the output of self.task into an expected_output table.

        This expected_output table should be used by the task VerifyOutput when
        verifying the output of a task.

        Raises:
            TableMissingException: If the output table does not exist.

        """
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
