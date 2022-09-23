import pandas as pd
import matplotlib.pyplot as plt
import imageio as iio
import numpy as np
import seaborn as sns

from algocomponents.tasks import Task, SQLTask, VisualizeDataset, AdapterTask
from algocomponents.adapters import GCPAdapter


class VisualizeDatasetTask(AdapterTask):

    def __init__(
        self,
        input_table_file_path: str = None,
        input_table_name: str = None,
        output_folder: str = "plots",
        **kwargs,
    ):
        super().__init__(**kwargs)

        self.output_folder = output_folder
        self.input_table_file_path = input_table_file_path
        self.input_table_name = input_table_name

        assert (
            self.input_table_file_path or self.input_table_name
        ), "VisualizeDatasetTask Must get either input_table_file_path or input_table_name, got neither."

        if self.input_table_file_path:
            self.df = pd.read_csv(f"{self.input_table_file_path}", sep=";")
        elif self.input_table_name:
            sql_string = f"SELECT * FROM `{self.input_table_name}`"
            gcp_adapter = GCPAdapter(config=None)
            sql_task_df = SQLTask(sql_string=sql_string, sql_adapter=gcp_adapter)
            self.df = sql_task_df.start().as_pandas()

    def run(self):

        visualize_data = VisualizeDataset(
            input_df=self.df,
            output_folder=self.output_folder)
        visualize_data.start()
