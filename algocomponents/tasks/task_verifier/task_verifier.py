from algocomponents.tasks import Task
import google

class VerifyTask:
    """
    Task that can either store or verify the output of another task
    """
    
    def __init__(
        self,
        task: Task,
        tasks_output_table: str,
        output_table: str,
        setup: bool,
    ):
        self.task = task
        self.tasks_output_table = tasks_output_table # where the task's output table is
        self.output_table = output_table # where should the output be saved
        self.setup = setup

    def start(self):
        self.task.start()
        adapter = self.task.sql_adapter
        adapter.connect()
        # check that the the output table exists
        assert adapter.table_exists(self.tasks_output_table), "Output table doesn't exists"

        if self.setup:
            # copy the table
            adapter.run_sql_string(f"""
                CREATE TABLE `{self.output_table}`
                CLONE `{self.tasks_output_table}`;
            """)
            print(f"Succesfully ran the setup to the output table: {self.output_table}")
        else:
            # check if table with the expected output exists
            if adapter.table_exists(self.output_table):
                # compare the tables, if the query returns no rows then the data is exactly the same.
                # if tables contain different amount of columns it will throw on error, if they contain different amount of rows, the differences are printed
                try:
                    adapter.run_sql_string(f"""
                        (
                        SELECT * FROM  `{self.output_table}`
                        EXCEPT DISTINCT
                        SELECT * from `{self.tasks_output_table}`
                        )
                        UNION ALL
                        (
                        SELECT * FROM `{self.tasks_output_table}`
                        EXCEPT DISTINCT
                        SELECT * from  `{self.output_table}`
                        )
                    """)
                except google.api_core.exceptions.BadRequest:
                    print("Tables doesn't match")
                    
            else:
                print("You must run setup first")
        
        adapter.disconnect()

