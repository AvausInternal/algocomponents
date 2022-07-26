import sqlite3
from configparser import ConfigParser
from typing import List

from algocomponents.adapters import SQLAdapter


class LocalSqliteAdapter(SQLAdapter):
    """Used to run queries locally.

    This adapter exists to be able to run queries locally for development
    purposes. Such as mocking a number of queries, testing out a pipeline
    structure, etc.
    """

    db_file = "local_sqlite.db"

    def __init__(self, config: ConfigParser = None):
        super().__init__(overriding_config=config)
        self.db_path = self.db_file
        self.connection = None
        self.cursor = None

    def connect(self):
        super().connect()
        self.connection = sqlite3.connect(self.db_path)
        self.cursor = self.connection.cursor()
        self.logger.info(sqlite3.version)

    def is_connected(self):
        if self.cursor is None:
            return False
        try:
            self.cursor.execute("SELECT 1")
            return True
        except sqlite3.ProgrammingError:
            return False

    def disconnect(self):
        self.connection.close()
        super().disconnect()

    def _format_table_name(self, table: str):
        return table.replace("`", "").replace(".", "_")

    def table_exists(self, table: str) -> bool:
        formatted_table = self._format_table_name(table)
        tables = self.cursor.execute(
            f"SELECT name FROM sqlite_master WHERE type='table' AND name='{formatted_table}'"
        ).fetchall()
        return len(tables) > 0

    def get_table_columns(self, table: str) -> List[str]:
        formatted_table = self._format_table_name(table)
        description = self.cursor.execute(
            f"SELECT * FROM {formatted_table}"
        ).description
        columns_names = [column[0] for column in description]
        return columns_names

    def _run_formatted_sql(self, sql: str):
        query_job = self.cursor.execute(sql)
        self.rows = self.cursor.fetchall()
        if query_job.description:
            self.columns = [column[0] for column in query_job.description]

        if self.rows:
            self.logger.info("Result")
            for row in self.rows:
                self.logger.info(row)

    def query_job_as_pandas(self):
        import pandas

        return pandas.DataFrame.from_records(
            data=self.rows,
            columns=self.columns,
        )

    def query_job_as_csv(self, path: str):
        dataframe = self.query_job_as_pandas()
        dataframe.to_csv(path)
