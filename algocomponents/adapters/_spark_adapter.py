from typing import List

from algocomponents.adapters import SQLAdapter


class SparkAdapter(SQLAdapter):
    """Used to run queries in spark.

    This adapter functions when running queries in Databricks as well.

    """

    def __init__(
        self,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.spark = None
        self.sdf = None

    def connect(self):
        """Connects the adapter.

        This method imports the pyspark dependencies: Therefore, pyspark is not
        a required the installation unless this adapter is used.

        The connection is stored in self.spark.

        """
        super().connect()
        from pyspark.sql import SparkSession

        self.spark = SparkSession.builder.getOrCreate()

    def is_connected(self):
        """Checks whether the adapter is connected.

        As long as self.spark is not None, the adapter is considered connected.

        """
        return self.spark is not None

    def disconnect(self):
        """Disconnects the adapter.

        Done by stopping the spark context and setting self.spark to None.

        """
        self.spark.stop()
        self.spark = None
        super().disconnect()

    def _format_table_name(self, table: str):
        """Performs an adapter-specific formatting of the table.

        For this adapter, this method does not change the table in any way.

        Args:
            table: The table to format.

        """
        return table

    def table_exists(self, table: str) -> bool:
        """Checks whether a table exists.

        Args:
            table: The table to look for.

        """
        table = self._format_table_name(table=table)
        database, table = table.split(".")
        sql_tables = self.run_sql_string(f"SHOW TABLES in `{database}`")[0].filter(
            f"tableName = '{table}'"
        )
        return sql_tables.count() > 0

    def get_table_columns(self, table: str) -> List[str]:
        """Gets the columns of a table.

        Args:
            table: The table to look at.

        """
        database, table = table.split(".")
        columns = self.spark.catalog.listColumns(tableName=table, dbName=database)
        columns_names = [col[0] for col in columns]
        return columns_names

    def _run_formatted_query(self, query: str):
        """Runs a query towards BigQuery.

        Args:
            query: The query to run.

        """
        self.sdf = self.spark.sql(query)
        self.logger.info("Result: ")
        self.logger.info(self.sdf.show(self.max_rows_displayed))

        return self.sdf

    def latest_query_as_pandas(self):
        """Get the result of the latest query as a pandas dataframe.

        Raises NotImplementedError().

        """
        raise NotImplementedError()

    def pandas_df_as_table(self, df, table, overwrite=False):
        """Get the result of the latest query as a pandas dataframe.

        Raises NotImplementedError().

        Args:
            df: The pandas dataframe to put in a table.
            table: The table you want to create.
            overwrite: Whether to overwrite an existing table, defaults to False.

        """
        raise NotImplementedError()

    def insert_pandas_df_into_table(self, df, table):
        """Creates a table and puts a pandas dataframe in it.

        Raises NotImplementedError().

        Args:
            df: The pandas dataframe to insert into a table.
            table: The table where you want to insert it.

        """
        raise NotImplementedError()

    def latest_query_as_csv(self, path: str):
        """Get the result of the latest query as a csv file.

        Raises NotImplementedError().

        Args:
            path: The path to save the csv file to.

        """
        raise NotImplementedError()
