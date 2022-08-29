from configparser import ConfigParser
from typing import List

from algocomponents.adapters import SQLAdapter


class SparkAdapter(SQLAdapter):
    """Used to run queries in spark.

    This adapter functions when running queries in Databricks as well.
    """

    def __init__(
        self,
        config: ConfigParser = None,
        section: str = "DEFAULT",
    ):
        super().__init__(config=config, section=section)
        self.spark = None
        self.sdf = None

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

    def _table_exists_implementation(self, table: str) -> bool:
        database, table = table.split(".")
        sql_tables = self.spark.sql(f"SHOW TABLES in `{database}`").filter(
            f"tableName = '{table}'"
        )
        return sql_tables.count() > 0

    def _get_table_columns_implementation(self, table: str) -> List[str]:
        database, table = table.split(".")
        columns = self.spark.catalog.listColumns(tableName=table, dbName=database)
        columns_names = [col[0] for col in columns]
        return columns_names

    def _run_formatted_query(self, query: str):
        self.sdf = self.spark.sql(query)
        self.sdf.show()

    def latest_query_as_pandas(self):
        raise NotImplementedError()

    def latest_query_as_csv(self, path: str):
        raise NotImplementedError()
