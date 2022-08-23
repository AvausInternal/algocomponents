from configparser import ConfigParser
from algocomponents.adapters import SQLAdapter
from typing import List


class SparkAdapter(SQLAdapter):
    """Used to run queries in spark.

    This adapter functions when running queries in Databricks as well.
    """

    def __init__(self, config: ConfigParser = None):
        super().__init__(overriding_config=config)
        self.spark = None

    def connect(self):
        super().connect()
        from pyspark.sql import SparkSession

        self.spark = SparkSession.builder.getOrCreate()

    def is_connected(self):
        return self.spark is not None

    def disconnect(self):
        self.spark.stop()
        self.spark = None
        super().disconnect()

    def _format_table_name(self, table: str):
        return table

    def table_exists(self, table: str) -> bool:
        database, table = table.split(".")
        sql_tables = self.spark.sql(f"SHOW TABLES in `{database}`").filter(
            f"tableName = '{table}'"
        )
        return sql_tables.count() > 0

    def get_table_columns(self, table: str) -> List[str]:
        database, table = table.split(".")
        columns = self.spark.catalog.listColumns(tableName=table, dbName=database)
        columns_names = [col[0] for col in columns]
        return columns_names

    def _run_formatted_sql(self, sql: str):
        sdf = self.spark.sql(sql)
        sdf.show()
