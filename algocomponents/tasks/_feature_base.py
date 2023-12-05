from abc import ABC, abstractmethod
from typing import List

from algocomponents.adapters.custom_exceptions import (
    TableMissingException,
    DataMismatchException,
)
from algocomponents.tasks import SQLPipeline


class FeatureBase(SQLPipeline, ABC):
    """An SQLPipeline that produces a Feature base.

    A Feature Base is two things:

        1. All combinations for a specific use case that should be scored. It
           can for example be all combinations of customers and products that
           are valid, taking all business rules into account, for some sendout.
        2. Everything required to calculate all features in said scoring. If for
           example when the sendout will occur, or what channel it will occur in
           is necessary for some features, these should be included.

    Properties:
        output_primary_keys: The primary keys of the output table.
        output_columns_created: All columns in the output table except for the primary keys.

    Args:
        output_table: Where this SQLPipeline writes it's results.

    """

    @property
    @abstractmethod
    def output_primary_keys(self) -> List[str]:
        pass

    @property
    @abstractmethod
    def output_columns_created(self) -> List[str]:
        pass

    def __init__(
        self,
        output_table: str,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.output_table = output_table.format(**self.config[self.section])
        self.add_to_config("output_table", self.output_table)

    def run(self):
        """Runs like an SQLPipeline, and then verifies the output table.

        It is verified that the output table exists, and that it contains the
        columns specified in the FeatureBase.

        """
        super().run()
        if not self.sql_adapter.table_exists(self.output_table):
            raise TableMissingException(
                f"Output table has not been created: {self.output_table}"
            )

        all_columns = self.output_primary_keys + self.output_columns_created
        output_columns = self.sql_adapter.get_table_columns(self.output_table)

        if not sorted(all_columns) == sorted(output_columns):
            raise DataMismatchException(
                f"Output table does not contain columns specified.\n"
                f"Output table: {self.output_table}\n"
                f"Has columns: {all_columns}\n"
                f"Should be output_primary_keys: {self.output_primary_keys}\n"
                f"and output_columns_created: {self.output_columns_created}"
            )
