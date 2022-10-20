from abc import ABC, abstractmethod
from configparser import ConfigParser
from typing import List

from algocomponents.adapters import SQLAdapter
from algocomponents.adapters.custom_exceptions import (
    TableMissingException,
    DataMismatchException,
)
from algocomponents.tasks import FeatureBase


class Feature(FeatureBase, ABC):
    """A feature that models can use to train and predict

    All features require an input table, and for every distinct combination of
    whichever columns are specified as input columns, the feature should be
    calculated. If for example your feature calculates the number of purchases
    customers have made some products (which can be ALL customers and ALL
    products), the input table should contain at least these two columns, and
    those two columns should be defined as input_columns.

    Then, the feature should output it's result into the output table, and the
    primary keys specified for the feature should be the primary keys of the
    output table.


    Properties:
        input_columns: What columns are necessary in the input table.
        output_primary_keys: The primary keys of the output table.
        output_columns_created: All columns in the output table except for the primary keys.

    Args:
        input_table: The table from which this SQLPipeline starts
        output_table: Where this SQLPipeline writes it's results

    """

    @property
    @abstractmethod
    def input_columns(self) -> List[str]:
        pass

    def __init__(
        self,
        input_table: str,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.input_table = input_table.format(**self.config[self.section])
        self.add_to_config("INPUT_TABLE", self.input_table)

    def startup(self):
        """Connects the adapter, and verifies the input table

        Checks whether the input-table exists, and that it has the columns
        specified in input_table_columns.

        """
        super().startup()
        if not self.sql_adapter.is_connected():
            self.sql_adapter.connect()

        if not self.sql_adapter.table_exists(self.input_table):
            raise TableMissingException(
                f"Input table does not exist: {self.input_table}"
            )

        input_table_columns = self.sql_adapter.get_table_columns(self.input_table)

        if not all(elem in self.input_columns for elem in input_table_columns):
            raise DataMismatchException(
                f"Input table does not contain all columns specified.\n"
                f"Input table: {self.input_table}\n"
                f"Has columns: {input_table_columns}\n"
                f"Should contain these columns: {self.input_columns}\n"
            )
