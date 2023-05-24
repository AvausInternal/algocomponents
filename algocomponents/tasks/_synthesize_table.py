import os

from algocomponents.tasks import Task, SQLTask
import pandas as pd

from typing import List


class SynthesizeTable(SQLTask):
    """A task that synthesizes and exports a table

    Uses GetSynthesizationQuery for the table and then runs it.

    Args:
        input_table: The table to synthesize
        hash_columns: The columns to hash when synthesizing. This is done on all
            columns that contain sensitive values.
        output_table: Where to put the synthesized data
        row_number_columns: Which columns to replace with an incremental index.
            Usually this is done to primary keys, as their actual numbers are of
            no value and it's just relevant that there is something to join on.
        overwrite: Whether to overwrite an existing table, defaults to False.
        max_distinct_values: Max number of distinct values to take per column
        max_rows: Max number of rows to output in total
    """

    def __init__(
        self,
        input_table: str,
        output_table: str,
        row_number_columns: List[str] = None,
        overwrite: bool = False,
        max_rows: int = 100,
        max_distinct_values: int = 20,
        hash_columns: List[str] = None,
        **kwargs,
    ):
        super().__init__(sql_string=" ", **kwargs)

        self.input_table = input_table
        self.output_table = output_table
        self.row_number_columns = row_number_columns or []
        self.overwrite = overwrite
        self.max_rows = max_rows
        self.max_distinct_values = max_distinct_values
        self.hash_columns = hash_columns or []

    def run(self):
        """Runs either the sql_string or the sql_file_path.

        If an sql_string is given, this takes priority. If an sql_file_path is
        given, the text inside it is parsed and then run using run_sql_string().

        """
        self.sql_string = self.get_synthesization_query()
        super().run()

    def get_synthesization_query(self) -> str:
        """Returns the result as a pandas dataframe.

        This method is intended for method cascading: task.start().as_pandas().

        Returns:
            The result of the task as a pandas dataframe.

        """
        table_columns = self.sql_adapter.get_table_columns(table=self.input_table)
        query = ""
        if self.overwrite:
            query += (
                f"DROP TABLE IF EXISTS {self.output_table};{os.linesep}{os.linesep}"
            )
        query += f"CREATE TABLE {self.output_table} AS{os.linesep}"

        query += "WITH"
        ctes = []
        for table_column in table_columns:
            if table_column in self.row_number_columns:
                ctes.append(f"{table_column}")
                query += f" {table_column} AS ({os.linesep}"
                query += f"    SELECT{os.linesep}"
                query += f"        ROW_NUMBER() OVER() AS {table_column}{os.linesep}"
            elif table_column in self.hash_columns:
                ctes.append(f"{table_column}_hashed_values")
                query += f" {table_column}_hashed_values AS ({os.linesep}"
                query += f"    SELECT DISTINCT{os.linesep}"
                query += f"        {self.sql_adapter.get_hash_sql_method(table_column)} AS {table_column}{os.linesep}"
            else:
                ctes.append(f"{table_column}_values")
                query += f" {table_column}_values AS ({os.linesep}"
                query += f"    SELECT DISTINCT{os.linesep}"
                query += f"        {table_column} AS {table_column}{os.linesep}"
            query += f"    FROM {self.input_table}{os.linesep}"
            query += (
                f"    ORDER BY {self.sql_adapter.get_random_sql_method()}{os.linesep}"
            )
            query += f"    LIMIT {self.max_distinct_values}{os.linesep}"
            query += f"),"

        query = query[:-1] + os.linesep

        query += f"SELECT{os.linesep}"
        query += f"    *{os.linesep}"
        query += f"FROM {ctes[0]}{os.linesep}"
        for cte, table_column in zip(ctes[1:], table_columns[1:]):
            query += f"CROSS JOIN {cte}{os.linesep}"
        query += f"ORDER BY {self.sql_adapter.get_random_sql_method()}{os.linesep}"
        query += f"LIMIT {self.max_rows}{os.linesep}"

        return query
