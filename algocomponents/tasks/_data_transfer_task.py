from algocomponents.adapters import SQLAdapter
from algocomponents.tasks import Task, SQLTask


class DataTransferTask(Task):
    """DataTransferTask transfers data across adapters.

    Remember that if you use the LocalSQLite adapter, the data will be stored
    on your computer. Only store data locally if you are allowed to do so.

    The task can only either take "from_table" as input or
    "sql_string/sql_file_path" as input.

    If "from_table" is given as input, the task copies the full table and saves
    it to the specified table.

    If "sql_string" or "sql_file_path" is given as input, the task copies the
    query result from one adapter and saves it to the specified table.

    If both "sql_string" and "sql_file_path" are given, sql_string takes
    priority.


    Args:
        from_adapter: The adapter we want to move data from.
        to_adapter: The adapter we want to move data to.
        from_table: The table we want to move data from.
        to_table: The table we want to move data too.
        sql_string: The sql string to run.
        sql_file_path: Where the sql file to be run is.
        overwrite: Whether to overwrite an existing table, defaults to False.

    """

    def __init__(
        self,
        from_adapter: SQLAdapter = None,
        to_adapter: SQLAdapter = None,
        from_table: str = None,
        to_table: str = None,
        sql_string: str = None,
        sql_file_path: str = None,
        overwrite: bool = False,
        **kwargs,
    ):
        if from_table is not None and (sql_string or sql_file_path) is not None:
            raise ValueError(
                "Please give a value for from_table or sql_string/sql_file_path, but not both"
            )

        super().__init__(**kwargs)

        self.sql_string = sql_string
        self.sql_file_path = sql_file_path
        self.from_adapter = from_adapter
        self.to_adapter = to_adapter
        self.from_table = from_table
        self.to_table = to_table
        self.overwrite = overwrite

        self.i_connected_the_from_adapter = False
        self.i_connected_the_to_adapter = False

    def startup(self):
        super().startup()

        if self.from_adapter and not self.from_adapter.is_connected():
            self.i_connected_the_from_adapter = True
            self.from_adapter.connect()

        if self.to_adapter and not self.to_adapter.is_connected():
            self.i_connected_the_to_adapter = True
            self.to_adapter.connect()

    def run(self):
        if self.from_table is not None:
            from_table_formatted = self.from_adapter.format_string(self.from_table)
            to_table_formatted = self.to_adapter.format_string(self.to_table)
            self.logger.info(
                f"Copying table: {self.from_table}, formatted as {from_table_formatted}, "
                f"using {self.from_adapter.class_name},"
                f"into table: {self.to_table}, formatted as {to_table_formatted}, "
                f"using adapter {self.to_adapter.class_name}"
            )
            dataframe = self.from_adapter.table_as_pandas_df(from_table_formatted)

            self.to_adapter.pandas_df_as_table(
                df=dataframe, table=to_table_formatted, overwrite=self.overwrite
            )

        else:
            self.logger.info(
                f"Copying query results from running sql_string to table: {self.to_table}({self.to_adapter.class_name})"
            )

            # Create pandas df from query
            dataframe = (
                SQLTask(
                    sql_string=self.sql_string,
                    sql_file_path=self.sql_file_path,
                    sql_adapter=self.from_adapter,
                )
                .start()
                .as_pandas()
            )
            # Create table from pandas df
            self.to_adapter.pandas_df_as_table(
                df=dataframe, table=self.to_table, overwrite=self.overwrite
            )

    def shutdown(self):
        if self.i_connected_the_from_adapter:
            self.from_adapter.disconnect()

        if self.i_connected_the_to_adapter:
            self.to_adapter.disconnect()
