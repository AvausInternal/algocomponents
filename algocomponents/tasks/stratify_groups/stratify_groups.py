from typing import List

from algocomponents.adapters import LocalSqliteAdapter
from algocomponents.adapters import SQLAdapter
from algocomponents.adapters.custom_exceptions import (
    TableMissingException,
    TableIsEmptyException,
    DataMismatchException,
)
from algocomponents.tasks import SQLPipeline


class StratifyGroups(SQLPipeline):
    """Given a table with a set of columns to order the table, a stratified
     table with intended number of groups returns.

    Args:
        sql_adapter: A SQL adapter to connect to designated database type
        input_table: The name for target table
        stratify_on: A set of columns to order the table
        n_groups: Number of groups to stratify the table
        output_table: The table name to be returned
        **kwargs: Arbitrary keyword arguments

    Returns:
        An ordered table with stratified groups

    """

    def __init__(
        self,
        sql_adapter: SQLAdapter,
        input_table: str,
        stratify_on: List[str],
        n_groups: int,
        output_table: str,
        **kwargs,
    ):
        if isinstance(sql_adapter, LocalSqliteAdapter):
            sql_folder = "sqlite"
        else:
            sql_folder = "sql"

        super().__init__(
            sql_adapter=sql_adapter,
            sql_folder=sql_folder,
            **kwargs,
        )

        self.input_table = input_table
        self.stratify_on = stratify_on
        self.n_groups = n_groups
        self.output_table = output_table

        self.add_to_config("input_table", input_table)
        self.add_to_config("stratify_on", ", ".join(stratify_on))
        self.add_to_config("n_groups", n_groups)
        self.add_to_config("output_table", output_table)

    def startup(self):
        super().startup()

        if not self.sql_adapter.table_exists(self.input_table):
            raise TableMissingException(
                f"Input table does not exist: {self.input_table}"
            )

        table_columns = self.sql_adapter.get_table_columns(self.input_table)
        if len(table_columns) == 0:
            self.logger.info(f"Input table is empty")
            raise TableIsEmptyException(f"Table {self.input_table} is empty")

        if self.n_groups > len(table_columns):
            n_groups = len(table_columns)
            self.logger.info(
                f"Adjusting stratification group to the maximum records in table: {n_groups}"
            )

        # Check the columns of dataframe against stratifying list
        for col in self.stratify_on:
            if col.strip() not in table_columns:
                raise DataMismatchException(
                    f"Table {self.input_table} does not have column {col}"
                )
