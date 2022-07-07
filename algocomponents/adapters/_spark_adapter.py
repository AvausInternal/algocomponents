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

    def table_exists(self, database: str, table: str) -> bool:
        """Tnis is divergent from all the other table_exists methods, in that it requires 2 inputs"""

        sql_tables = self.spark.sql(f"SHOW TABLES in `{database}`").filter(
            f"tableName = '{table}'"
        )
        return sql_tables.count() > 0

    def get_table_columns(self, database: str, table: str) -> List[str]:
        """Tnis is divergent from all the other get_table_columns methods, in that it requires 2 inputs"""

        col_names = self.spark.sql(f"SHOW COLUMNS IN `{table}` IN `{database}`")
        return col_names.rdd.map(lambda x: x[0]).collect()

    def _run_formatted_sql(self, sql: str):
        sdf = self.spark.sql(sql)
        sdf.show()
