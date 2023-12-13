from typing import List

from algocomponents.adapters import SQLAdapter
from algocomponents.adapters.custom_exceptions import TableMissingException
from algocomponents.utils import require_connection


class SparkAdapter(SQLAdapter):
    """Used to run queries in spark.

    Using this in notebooks might not work as some notebooks set up a spark
    variable automatically using SparkSession, which this adapter may interfere
    with. In case it does not work, consider creating a new class that
    overwrites the connect(), is_connected() and disconnect()-methods.

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

    def is_connected(self) -> bool:
        """Checks whether the adapter is connected.

        As long as self.spark is not None, the adapter is considered connected.

        Returns:
            True if self.spark is not None, False otherwise.

        """
        return self.spark is not None

    @require_connection
    def disconnect(self):
        """Disconnects the adapter.

        Done by stopping the spark context and setting self.spark to None.

        """
        self.spark.stop()
        self.spark = None
        super().disconnect()

    def _format_table_name(self, table: str) -> str:
        """Performs an adapter-specific formatting of the table.

        For this adapter, this method does not change the table in any way.

        Args:
            table: The table to format.

        Returns:
            The formatted table (no change for this adapter).

        """
        return table

    @require_connection
    def table_exists(self, table: str) -> bool:
        """Checks whether a table exists.

        Args:
            table: The table to look for.

        Returns:
            True if the table exists, false otherwise.

        """
        table = self._format_table_name(table=table)
        database, table = table.split(".")
        sql_tables = self.run_sql_string(f"SHOW TABLES in `{database}`")[0].filter(
            f"tableName = '{table}'"
        )
        return sql_tables.count() > 0

    @require_connection
    def get_table_columns(self, table: str) -> List[str]:
        """Gets the columns of a table.

        Args:
            table: The table to look at.

        Returns:
            A list of strings containing the names of the columns in the table.

        """
        database, table = table.split(".")
        columns = self.spark.catalog.listColumns(tableName=table, dbName=database)
        columns_names = [col[0] for col in columns]
        return columns_names

    @require_connection
    def _run_formatted_query(self, query: str):
        """Runs a query towards BigQuery.

        The return-statement is not type hinted to a spark dataframe as that
        would require importing the library.

        Args:
            query: The query to run.

        Returns:
            A spark dataframe of the result.

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

    @require_connection
    def pandas_df_as_table(self, df, table, overwrite=False):
        """Get the result of the latest query as a pandas dataframe.

        Raises NotImplementedError().

        Args:
            df: The pandas dataframe to put in a table.
            table: The table you want to create.
            overwrite: Whether to overwrite an existing table, defaults to False.

        """
        raise NotImplementedError()

    @require_connection
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

    @require_connection
    def count_rows_in_table(self, table: str) -> int:
        """Count the number of rows in a table

        Args:
            table (str): The table to count number of rows

        Raises:
            TableMissingException: if table does not exist

        Returns:
            int: number of rows in table
        """
        if not self.table_exists(table):
            raise TableMissingException(f"Table {table} does not exist.")
        else:
            row_count_query = f"SELECT count(*) as row_count FROM {table}"
            return int(self.run_sql_string(row_count_query)[0].first()[0])
