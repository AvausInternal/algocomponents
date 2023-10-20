import numpy as np

from typing import List
from algocomponents.tasks import Task


class PartiallyRandomizeScores(Task):
    """A task for partially randomizing scores 
    
    This is usually done when the model prediction is done
    and we want a certain subset of unique entiites to have random scores.
    It is basically an A/B test for checking the model impact.
    """
    
    def __init__(
        self,
        input_table: str,
        randomized_people_table: str,
        output_table: str,
        identifier_columns: List[str],
        randomized_percentage: float = 0.2,
        segment_column: str = "segment",
        chunks_number=10,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.input_table = input_table
        self.randomized_people_table = randomized_people_table
        self.output_table = output_table
        self.identifier_columns = identifier_columns
        self.randomized_percentage = randomized_percentage
        self.segment_column = segment_column
        self.chunks_number = chunks_number

    def run(self):
        df = self.sql_adapter.table_as_pandas_df(self.input_table)
        randomized_df, subset_df = self._randomize_dataframe(df)
        self.sql_adapter.pandas_df_as_table(
            df=randomized_df,
            table=self.output_table,
            overwrite=True,
            chunks_number=self.chunks_number,
        )
        subset_df = subset_df[self.identifier_columns]
        self.sql_adapter.pandas_df_as_table(
            df=subset_df,
            table=self.randomized_people_table,
            overwrite=True,
            chunks_number=self.chunks_number,
        )

    def _randomize_dataframe(self, df):
        subset_size = int(
            len(df.groupby(self.identifier_columns)) * self.randomized_percentage
        )
        subset = df.drop_duplicates(subset=self.identifier_columns).sample(subset_size)
        all_segments = df[self.segment_column].unique()
        subset[self.segment_column] = np.random.choice(all_segments, size=len(subset))
        df = df.set_index(self.identifier_columns)
        subset = subset.set_index(self.identifier_columns)
        df.update(subset)
        return df.reset_index(), subset.reset_index()
