"""Creates a couple of plots with AvausVisualizer for visual inspection.

As there is not programmatic way to test that plots "look good", this script
exists as a way to quickly generate a bunch of example plots to look for visual
errors or room for improvement in the visualization.

"""

import os

import pandas as pd

from algocomponents.adapters import LocalSqliteAdapter
from algocomponents.tasks import (
    VisualizeFeatures,
)

output_folder = os.path.join("tests", "avaus_visuals_examples", "plots")
input_table = "avaus_visuals_test_data"
input_table_df = pd.DataFrame(
    data={
        "cat_1": ["a", "b", "c", "a", "b", "c", "a", "b", "c"],
        "cat_2": ["p", "q", "q", "p", "q", "p", "p", "p", "q"],
        "cont_1": [0.1, 0.3, 0.3, 0.7, 0.4, 0.2, 0.0, 0.6, 0.9],
        "cont_2": [0.9, 0.0, 0.0, 0.1, 0.4, 0.2, 0.4, 0.0, 0.4],
        "target_label": [0, 1, 1, 0, 1, 0, 1, 1, 0],
    }
)
sql_adapter = LocalSqliteAdapter()
sql_adapter.connect()
sql_adapter.pandas_df_as_table(df=input_table_df, table=input_table, overwrite=True)
VisualizeFeatures(
    sql_adapter=sql_adapter,
    input_table=input_table,
    target_label_column="target_label",
    categorical_feature_columns=["cat_1", "cat_2"],
    continuous_feature_columns=["cont_1", "cont_2"],
    output_folder=output_folder,
).start()
sql_adapter.disconnect()
