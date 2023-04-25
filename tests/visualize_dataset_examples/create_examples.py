"""Runs VisualizeDataset on an example pandas dataframe for visual inspection.

As there is not programmatic way to test that plots "look good", this script
exists as a way to quickly generate a bunch of example plots to look for visual
errors or room for improvement in the visualization.

"""

import os

import pandas as pd

from algocomponents.tasks import (
    VisualizeDataset,
)

output_folder = os.path.join("tests", "visualize_dataset_examples", "plots")
input_table = "avaus_visuals_test_data"
input_table_df = pd.DataFrame(
    data={
        "cat_1": ["a", "b", "c", "a", "a", "c", "b", "b", "b"],
        "cat_2": ["p", "q", "q", "p", "q", "p", "p", "p", "q"],
        "cont_1": [0.1, 0.3, 0.3, 0.7, 0.4, 0.2, 0.0, 0.6, 0.9],
        "cont_2": [1, 3, 3, 7, 4, 2, 0, 6, 9],
        "cont_3": [9, 0, 0, 1, 4, 0, 4, 4, 2],
        "target_label": [0, 1, 1, 0, 1, 0, 1, 1, 0],
    }
)
VisualizeDataset(
    input_df=input_table_df,
    continuous_features=["cont_1", "cont_2", "cont_3"],
    categorical_features=["cat_1", "cat_2"],
    output_folder=output_folder,
).start()
