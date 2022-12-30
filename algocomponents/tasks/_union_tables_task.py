import os
from typing import List

from algocomponents.adapters.custom_exceptions import (
    TableMissingException,
    DataMismatchException,
)
from algocomponents.tasks import SQLTask


class UnionTablesTask(SQLTask):
    """Performs the UNION ALL operation on all supplied tables.

    This task first verifies that the tables have the same columns and column
    names, then puts them all in the same table using UNION ALL.

    Args:
        tables: Which tables to union, written as database.table.
        task_output_table: The output table for the task.
        expected_output_table: Where we want to save the expected output.

    """

    def __init__(
        self,
        tables: List[str],
        output_table: str,
        overwrite_output_table_if_exists: bool = True,
        **kwargs,
    ):
        if len(tables) == 0:
            raise ValueError("Cannot union 0 tables (cannot construct output table)")

        self.overwrite_output_table_if_exists = overwrite_output_table_if_exists
        self.tables = tables
        sql_string = self.generate_union_query(
            tables=tables,
            overwrite_output_table_if_exists=overwrite_output_table_if_exists,
        )

        super().__init__(
            sql_string=sql_string,
            **kwargs,
        )
        self.add_to_config("output_table", output_table)

    @staticmethod
    def generate_union_query(
        tables: List[str], overwrite_output_table_if_exists: bool = True
    ) -> str:
        """Generates the query that will union all the tables.

        Args:
            tables: List of strings of tables to union.
            overwrite_output_table_if_exists: If existing tables are overwritten.

        Returns:
            The query that will union all tables.

        """
        query = ""
        for table in tables:
            if query == "":
                query = f"SELECT * FROM {table}"
            else:
                query += f"{os.linesep}UNION ALL" f"{os.linesep}SELECT * FROM {table}"

        query = (
            """CREATE TABLE {output_table} AS
        """
            + query
        )

        if overwrite_output_table_if_exists:
            query = (
                """DROP TABLE IF EXISTS {output_table};
            """
                + query
            )

        return query

    def startup(self):
        """Connects the sql_adapter and verifies that the table exists.

        Also runs a check that all the tables that should be union:ed contain
        the same columns.

        """
        self.sql_adapter.connect()
        columns = []
        for table in self.tables:
            if not self.sql_adapter.table_exists(table):
                raise TableMissingException(f"Table missing in union task: {table}")

            current_column_names = self.sql_adapter.get_table_columns(table)
            if len(columns) == 0:
                columns = current_column_names
            elif columns != current_column_names:
                raise DataMismatchException(
                    "Tables do not share the exact same columns: \n"
                    f"{columns} \n"
                    f"{current_column_names}"
                )
