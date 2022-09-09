import os
from sqlite3 import OperationalError
from google.api_core.exceptions import BadRequest

from algocomponents.adapters import GCPAdapter, SparkAdapter
from algocomponents.tasks import Task

class VerifyTask(Task):
    """
    Task that can either store or verify the output of another task
    """
    
    def __init__(
        self,
        task: Task,
        tasks_output_table: str,
        output_table: str,
        setup: bool,
        **kwargs,
    ):
        super().__init__(**kwargs)

        self.task = task
        self.setup = setup
        self.output_table = output_table
        self.tasks_output_table = tasks_output_table
        self.sql_folder = os.path.join(self.classpath, "sql")

        # GCP and Spark supports only "EXCEPT DISTINCT" and sqlite support only "EXCEPT"
        if type(self.task.sql_adapter) == GCPAdapter or type(self.task.sql_adapter) == SparkAdapter :
            distinct = "DISTINCT"
        else:
            distinct = ""
        self.format_variables = {"DISTINCT_" : distinct, "EXPECTED_OUTPUT_TABLE" : output_table, "TASK_OUTPUT_TABLE" : tasks_output_table}


    def start(self):
        self.task.start()
        adapter = self.task.sql_adapter
        adapter.connect()

        # check that the task's output table exists
        if not adapter.table_exists(self.tasks_output_table):
            raise Exception("Output table doesn't exists")

        if self.setup:
            adapter.run_sql_file(os.path.join(self.sql_folder, "save_expected_table.sql"), self.format_variables)
            self.logger.info(f"Succesfully ran the setup to the output table: {self.output_table}")
        else:
            # check if table with the expected output exists
            if adapter.table_exists(self.output_table):
                try:
                    # make sql query that compares tables and returns mismatching rows
                    result = adapter.run_sql_file(os.path.join(self.sql_folder, "compare_two_tables.sql"), self.format_variables)
                    if len(result[0]) != 0:
                        raise Exception("Tables Doesn't match")
                    else:
                        self.logger.info("Tables match")
                # throws an error since table comparison doesn't support array cols
                except (BadRequest, OperationalError) as e:
                    raise Exception("Tables doesn't match or tables contain array columns which are not supported", e) from None
            else:
                raise Exception("You must run the setup first")
        
        adapter.disconnect()
        
