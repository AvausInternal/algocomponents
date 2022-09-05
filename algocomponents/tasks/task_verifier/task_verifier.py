from algocomponents.tasks import Task, SQLPipeline
from algocomponents.adapters import GCPAdapter, LocalSqliteAdapter

from google.api_core.exceptions import BadRequest
from sqlite3 import OperationalError

class VerifyTask(SQLPipeline):
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
        self.tasks_output_table = tasks_output_table # where the task's output table is
        self.output_table = output_table # where should the output be saved
        self.setup = setup

    def start(self):
        self.task.start()
        adapter = self.task.sql_adapter
        adapter.connect()
        # check that the output table exists
        assert adapter.table_exists(self.tasks_output_table), "Output table doesn't exists"

        if self.setup:
            # if setup is ran again we delete the old table first
            if adapter.table_exists(self.output_table):
                pass
            # copy the table
            if type(adapter) == GCPAdapter:
                adapter.run_sql_string(f"""
                    CREATE TABLE `{self.output_table}`
                    CLONE `{self.tasks_output_table}`;
                """)
            elif type(adapter) == LocalSqliteAdapter:
                adapter.run_sql_string(f"""
                    CREATE TABLE `{self.output_table}` AS SELECT * FROM `{self.tasks_output_table}`
                """)
            else:
                raise NotImplementedError("This adapter is not yet supported")

            self.logger.info(f"Succesfully ran the setup to the output table: {self.output_table}")
        else:
            # check if table with the expected output exists
            if adapter.table_exists(self.output_table):
                # compare the tables, if the query returns no rows then the data is exactly the same.
                # if tables contain different amount of columns it will throw on error
                try:
                    if type(adapter) == GCPAdapter:
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
                        result = adapter.query_job.result().total_rows != 0

                    elif type(adapter) == LocalSqliteAdapter:
                        adapter.run_sql_string(f"""
                            SELECT * FROM (SELECT * FROM `{self.output_table}`
                                        EXCEPT
                                        SELECT * FROM `{self.tasks_output_table}`)
                            UNION ALL
                            SELECT * FROM (SELECT * FROM `{self.tasks_output_table}`
                                        EXCEPT
                                        SELECT * FROM `{self.output_table}`)
                        """)
                        result = adapter.rows
                    else:
                        raise NotImplementedError("This adapter is not yet supported")

                    if result:
                        self.logger.info("Tables doesn't match")
                    else:
                        self.logger.info("Tables match")

                # Different number of columns or array columns
                except (BadRequest, OperationalError) as e:
                    print(e)
                    self.logger.info("Tables doesn't match or tables contain arrays")
            else:
                self.logger.info("You must run setup first")
        
        adapter.disconnect()

