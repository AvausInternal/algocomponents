from itertools import product
from random import shuffle
from typing import List

import pandas as pd

from algocomponents.tasks import Task


class SynthesizeTable(Task):
    """A task that synthesizes and exports a table

    Args:
        input_table: The table to synthesize
        hash_columns: The columns to hash when synthesizing. This is done on all
            columns that contain sensitive values.
        output_table: Where to put the synthesized data
        row_number_columns: Which columns to replace with an incremental index.
            Usually this is done to primary keys, as their actual numbers are of
            no value and it's just relevant that there is something to join on.
        overwrite: Whether to overwrite an existing table, defaults to False.
        max_values_per_column: Max number of distinct values to take per column
        max_rows: Max number of rows to output in total
    """

    def __init__(
        self,
        input_table: str,
        output_table: str,
        row_number_columns: List[str] = None,
        overwrite: bool = False,
        max_rows: int = 100,
        max_values_per_column: int = 20,
        hash_columns: List[str] = None,
        **kwargs,
    ):
        super().__init__(**kwargs)

        self.input_table = input_table
        self.output_table = output_table
        self.row_number_columns = row_number_columns or []
        self.overwrite = overwrite
        self.max_rows = max_rows
        self.max_values_per_column = max_values_per_column
        self.hash_columns = hash_columns or []

    def run(self):
        df = self.sql_adapter.table_as_pandas_df(self.input_table)
        distinct_values = {}

        for column in df.columns:
            distinct_values[column] = df[column].unique()[: self.max_values_per_column]

        cross_join = list(product(*list(distinct_values.values())))

        shuffle(cross_join)
        df = pd.DataFrame(
            cross_join[: self.max_rows], columns=list(distinct_values.keys())
        )

        for column in self.row_number_columns:
            df[column] = df.index % self.max_values_per_column

        for column in self.hash_columns:
            df[column] = df[column].astype(str).apply(hash)

        self.sql_adapter.pandas_df_as_table(
            df=df, table=self.output_table, overwrite=self.overwrite
        )
