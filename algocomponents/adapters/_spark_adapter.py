from configparser import ConfigParser

from algocomponents.adapters import SQLAdapter


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

    def _run_formatted_sql(self, sql: str):
        sdf = self.spark.sql(sql)
        sdf.show()
