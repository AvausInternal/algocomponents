from task_classes.local_sqlite_adapter import LocalSqliteAdapter
from task_classes.sql_adapter import SQLAdapter
from task_classes.task import Task


class SQLTask(Task):
    """A task used to run SQL queries with an adapter.

    The sql_file_path is the path to the file from the project root. The SQLTask
    will use whatever adapter supplied to create the connection and run the sql
    queries, or default to using the LocalSqliteAdapter.
    """

    def __init__(
            self,
            sql_file_path: str,
            sql_adapter: SQLAdapter = None,
            section: str = None,
    ):
        super().__init__(section=section)
        self.sql_adapter = sql_adapter or LocalSqliteAdapter(self.config)
        self.sql_file_path = sql_file_path

    def startup(self):
        self.sql_adapter.connect()

    def run(self):
        self.sql_adapter.run_sql_file(
            path=self.sql_file_path,
            format_variables=dict(self.config[self.section]),
        )

    def shutdown(self):
        self.sql_adapter.disconnect()
