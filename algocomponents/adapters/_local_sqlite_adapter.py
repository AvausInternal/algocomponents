import os
import sqlite3
from configparser import ConfigParser

from definitions import ALGO_COMPONENTS_ROOT_DIR
from algocomponents.adapters.sql_adapter import SQLAdapter


class LocalSqliteAdapter(SQLAdapter):
    """Used to run queries locally.

    This adapter exists to be able to run queries locally for development
    purposes. Such as mocking a number of queries, testing out a pipeline
    structure, etc.
    """

    db_file = "local_sqlite.db"

    def __init__(self, config: ConfigParser = None):
        super().__init__(overriding_config=config)
        self.db_path = os.path.join(ALGO_COMPONENTS_ROOT_DIR, self.db_file)
        self.connection = None
        self.cursor = None

    def connect(self):
        self.logger.info(f"LocalSqliteAdapter establishing connection...")
        self.connection = sqlite3.connect(self.db_path)
        self.cursor = self.connection.cursor()

    def check_connection(self):
        self.logger.info(self.connection)
        self.logger.info(sqlite3.version)

    def disconnect(self):
        self.connection.close()
        self.logger.info(f"LocalSqliteAdapter disconnected.")

    def run_sql(self, sql: str):
        sql = sql.strip()
        self.logger.info(f"Executing the following query: \n{sql}")

        self.cursor.execute(sql)
        rows = self.cursor.fetchall()

        if rows:
            self.logger.info("Result")
            for row in rows:
                self.logger.info(row)
