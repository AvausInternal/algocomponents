import numpy as np
import pandas as pd
from joblib import Parallel, delayed


class TestGroupSplitter:
    def __init__(
            self,
            customer_df: pd.DataFrame,
            customer_key: str,
            fractions: tuple,
            group_names: tuple,
            strat_columns: list = [],
    ):
        self.customer_df = customer_df
        self.customer_key = customer_key
        self.fractions = fractions
        self.group_names = group_names
        self.strat_columns = strat_columns

    def split(self):
        if sum(self.fractions) < 0.99:
            raise ValueError('Fractions must sum to 1!')
        segments = self.customer_df[[self.customer_key] + self.strat_columns]
        segments['rand_col'] = np.random.rand(len(segments))
        if self.strat_columns:
            segments['rank'] = segments.groupby(self.strat_columns)['rand_col'].rank(pct=True)
        else:        
            segments['rank'] = segments[self.customer_key].rank(pct=True)  
            
        boundaries = self._get_boundaries(self.fractions, self.group_names)
        segments['group_name'] = segments['rank']\
            .apply(self._apply_split, boundaries=boundaries)
        
        segments.rename(columns={self.customer_key: 'customer_key'}, inplace=True)
        segments = segments[['group_name', 'customer_key']]
        return segments
            
    def _get_boundaries(self, fractions, group_names):
        cutoff = 0
        boundaries = []
        for n in range(len(group_names)):
            f = fractions[n]
            boundaries.append((group_names[n], cutoff, cutoff + f))
            cutoff = cutoff + f
        return boundaries
    
    def _apply_split(self, value, boundaries):
        for (name, lower, upper) in boundaries:
            if value >= lower and value <= upper:
                return name