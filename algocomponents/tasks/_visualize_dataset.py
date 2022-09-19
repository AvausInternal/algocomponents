import pandas as pd
import matplotlib.pyplot as plt
import imageio as iio
import numpy as np
import seaborn as sns
from algocomponents.tasks import Task, SQLTask

class VisualizeDataset(Task):
    """A task that visualizes features
    given a dataset table"""

    def __init__(
        self,
        input_df: pd.DataFrame,
        # output_folder: str,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.input_df = input_df
        # self.output_folder = output_folder


    def run(self):
        print("dummy visualize dataset run")
        print(self.input_df)

        self.save_boxplot(self.input_df, "boxplot")
        self.normalize_df()
        self.save_boxplot(self.df_normalized, "boxplot_normalized")
        self.save_histogram(self.input_df, "histogram")



    def normalize_df(self):
        #dataframe with only numerical features
        self.df_numeric = self.input_df.select_dtypes(include=np.number)

        #dataframe with only numerical features and normalized values
        self.df_normalized = (self.df_numeric - self.df_numeric.min()) / (self.df_numeric.max() - self.df_numeric.min())


    def save_boxplot(self, data_frame, file_name):
        fig = plt.figure(figsize=(10, 7))
        sns.boxplot(data=data_frame)

        plt.savefig(f"{file_name}.png")
        print(f"Boxplot saved under \'{file_name}.png\' file")

    def save_histogram(self, data_frame, file_name):
        cols = data_frame.columns
        fig = plt.figure(figsize=(10, 7))
        for col in cols:
            sns.histplot(data=data_frame, x=col)

            plt.savefig(f"{file_name}_{col}.png")
            plt.clf()
            print(f"Histogram of a feature: \'{col}\' saved under \'{file_name}_{col}.png\' file")