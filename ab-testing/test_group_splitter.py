import numpy as np
import pandas as pd


class TestGroupSplitter:
    def __init__(
            self,
            customer_df: pd.DataFrame,
            customer_key: str,
            fractions: tuple,
            group_names: tuple
    ):
        self.customer_df = customer_df
        self.customer_key = customer_key
        self.fractions = fractions
        self.group_names = group_names

    def split(self):
        if sum(self.fractions) < 0.99:
            raise ValueError('Fractions must sum to 1!')
        segments = self.customer_df[[self.customer_key]]
        segments['randCol'] = np.random.rand(len(segments))
        segments['group_name'] = segments['randCol']\
            .apply(self._apply_split, fractions=self.fractions, group_names=self.group_names)
        segments.rename(columns={self.customer_key: 'customer_key'}, inplace=True)
        segments = segments[['group_name', 'customer_key']]
        return segments

    def _apply_split(self, x, fractions, group_names):
        LB = 0
        for i, f in enumerate(fractions):
            UB = LB + f
            if (x >= LB) & (x < UB):
                return group_names[i]
            LB = UB
