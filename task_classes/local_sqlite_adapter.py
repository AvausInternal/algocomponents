import os
import sqlite3

from definitions import ALGO_FACTORY_ROOT_DIR
from task_classes.sql_adapter import SQLAdapter


class LocalSqliteAdapter(SQLAdapter):
    """Used to run queries locally.

    This adapter exists to be able to run queries locally for development
    purposes. Such as mocking a number of queries, testing out a pipeline
    structure, etc.
    """

    db_file = "local_sqlite.db"

    def __init__(self, config):
        super().__init__(overriding_config=config)
        self.db_path = os.path.join(ALGO_FACTORY_ROOT_DIR, self.db_file)
        self.connection = None
        self.cursor = None

    def connect(self):
        self.connection = sqlite3.connect(self.db_path)
        self.cursor = self.connection.cursor()

    def check_connection(self):
        self.logger.info(self.connection)
        self.logger.info(sqlite3.version)

    def disconnect(self):
        self.connection.close()

    def run_sql(self, sql: str):
        sql = sql.strip()
        self.logger.info("Executing the following query:")
        for sql_row in sql.split("\n"):
            self.logger.info(sql_row)

        self.cursor.execute(sql)
        rows = self.cursor.fetchall()

        if rows:
            self.logger.info("Result")
            for row in rows:
                self.logger.info(row)
