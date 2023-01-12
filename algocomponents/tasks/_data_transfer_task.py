from algocomponents.tasks import SQLTask
from algocomponents.adapters import SQLAdapter


class DataTransferTask(SQLTask):
    """Copies the query result from one adapter and saves it to the specified table.
        
    The task can be used to copy query results within the same adapter or
    transfer data across adapters.   

    Runs either the sql_string or the sql_file_path; if an sql_string is given, this 
    takes priority. 

    Args:
        from_adapter: The adapter we want to move data from. LocalSqliteAdapter and BigQueryAdaper are supported.
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
        super().__init__(**kwargs,sql_file_path=sql_file_path,sql_string=sql_string)

        self.from_adapter = from_adapter
        self.to_adapter = to_adapter
        self.from_table = from_table
        self.to_table = to_table
        self.overwrite = overwrite

    def run(self):
        
        self.logger.info(f"Copying query results from table: {self.from_table}({self.from_adapter.class_name}) to table: {self.to_table}({self.to_adapter.class_name})")
        
        #Create pandas df from query
        dataframe = (
            SQLTask(
                sql_string=self.sql_string,
                sql_file_path= self.sql_file_path,
                sql_adapter=self.from_adapter,
            ).start().as_pandas()
        )
        #Create table from pandas df 
        self.to_adapter.connect()
        self.to_adapter.pandas_df_as_table(df= dataframe, table=self.to_table , overwrite= self.overwrite)
        