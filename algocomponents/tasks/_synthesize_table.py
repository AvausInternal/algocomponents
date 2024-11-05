import random
from datetime import timedelta
from typing import List

import pandas as pd

from algocomponents.tasks import Task
from algocomponents.utils._tools import deterministic_hash_int, deterministic_hash_str


class SynthesizeTable(Task):
    """A task that synthesizes and exports a table.

    A synthesized table ideally has the same structure as the original table,
    but has none of the sensitive information. Relations are removed by
    sampling from the individual columns, distributions are removed in the same
    operations and sensitive values should be hashed. This allows you to bring
    a synthesized version of a table outside the project you are working on, for
    example to allow people outside the project to write pipelines for the data,
    or to get help troubleshooting sql from someone outside the project.

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
        self.logger.info(
            f"Synthesizing table {self.input_table} into {self.output_table}"
        )
        df = self.sql_adapter.table_as_pandas_df(
            self.input_table, max_rows=self.max_rows
        )
        distinct_values = {}

        for column in df.columns:
            distinct_values[column] = df[column].unique()[: self.max_values_per_column]

        sampled_rows = []

        for _ in range(self.max_rows):
            sampled_row = [random.choice(distinct_values[col]) for col in df.columns]
            sampled_rows.append(sampled_row)

        synthesized_df = pd.DataFrame(
            sampled_rows, columns=list(distinct_values.keys())
        )

        synthesized_df = synthesized_df.sample(frac=1).reset_index(drop=True)

        for column in self.row_number_columns:
            synthesized_df[column] = synthesized_df.index % self.max_values_per_column

        two_years_in_seconds = 2 * 365 * 24 * 60 * 60
        end_date = pd.Timestamp.today().normalize()

        for column in self.hash_columns:
            original_dtype = synthesized_df[column].dtype

            if pd.api.types.is_integer_dtype(original_dtype):
                # In some cases, bool is saved as integers with the value 0 or 1
                # If this is such a column, only create such integers
                if df[column].max() <= 1 and df[column].min() >= 0:
                    synthesized_df[column] = synthesized_df[column].apply(
                        lambda x: deterministic_hash_int(x, column) % 2
                    )
                else:
                    synthesized_df[column] = synthesized_df[column].apply(
                        lambda x: deterministic_hash_int(x, column) % 1_000_00
                    )

            elif pd.api.types.is_float_dtype(original_dtype):
                synthesized_df[column] = synthesized_df[column].apply(
                    lambda x: (deterministic_hash_int(x, column) % 10_000) / 100.0
                )

            elif pd.api.types.is_bool_dtype(original_dtype):
                synthesized_df[column] = synthesized_df[column].apply(
                    lambda x: (deterministic_hash_int(x, column) % 2) == 0
                )

            elif pd.api.types.is_datetime64_any_dtype(original_dtype):
                synthesized_df[column] = synthesized_df[column].apply(
                    lambda x: end_date
                    - timedelta(
                        seconds=deterministic_hash_int(x, column) % two_years_in_seconds
                    )
                )

            else:
                synthesized_df[column] = synthesized_df[column].apply(
                    lambda x: deterministic_hash_str(x, column, length=16)
                )

        self.logger.info(
            f"Creating output table from dataframe:\n{synthesized_df.head()}"
        )

        self.sql_adapter.pandas_df_as_table(
            df=synthesized_df, table=self.output_table, overwrite=self.overwrite
        )
