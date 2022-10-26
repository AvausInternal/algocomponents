import pandas as pd
import numpy as np


from algocomponents.tasks import AdapterTask
from algocomponents.utils import save_boxplot, save_histogram, save_corr_matrix


class VisualizeDataset(AdapterTask):
    """A task that visualizes features given a dataset table.

    The task takes one of the following dataset sources as input:
    input_df, input_csv_file or input_table_name and save descriptive plots:
    boxplot, normalized boxplot, histograms, correlation matrix of that dataset.

    Attributes:
        input_df (pd.DataFrame, optional): Pandas DataFrame with dataset to visualize.
        input_csv_file (str, optional): Csv file path with dataset to visualize.
        input_table_name (str, optional): Database table name with dataset to visualize
            following "{DATASET}.{TABLE}" naming convention.
        output_folder (str, optional): Folder name or folder path, where plots are to be saved.
        interactive_plots (bool, optional): Whether to additionally save interactive plots.

    """

    def __init__(
        self,
        input_df: pd.DataFrame = None,
        input_csv_file: str = None,
        input_table_name: str = None,
        output_folder: str = "",
        interactive_plots: bool = True,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.input_df = input_df
        self.input_csv_file = input_csv_file
        self.input_table_name = input_table_name
        self.output_folder = output_folder
        self.interactive_plots = interactive_plots

        only_one_true_list = [
            self.input_csv_file is not None,
            self.input_table_name is not None,
            self.input_df is not None,
        ]
        if only_one_true_list.count(True) > 1:
            raise ValueError(
                "VisualizeDataset task must get only one dataset source: "
                "input_csv_file or input_table_name or input_df, got more."
            )
        elif only_one_true_list.count(True) < 1:
            raise ValueError(
                "VisualizeDataset task must get a dataset source: input_csv_file or input_table_name or input_df, "
                "got none."
            )

        if self.input_table_name and self.sql_adapter is None:
            raise ValueError("You must provide sql_adapter with input_table_name.")

        if self.input_df is not None and self.input_df.empty:
            raise ValueError("Input_df is empty.")

    def run(self):
        if self.input_csv_file:
            self.input_df = pd.read_csv(f"{self.input_csv_file}")
        elif self.input_table_name:
            self.input_df = self.sql_adapter.table_as_pandas_df(self.input_table_name)

        # dataframe with only numerical features
        self.df_numeric = self.input_df.select_dtypes(include=np.number)
        # dataframe with only numerical features and normalized values
        self.df_normalized = (self.df_numeric - self.df_numeric.min()) / (
            self.df_numeric.max() - self.df_numeric.min()
        )

        save_boxplot(
            df=self.df_numeric,
            output_folder=self.output_folder,
            interactive_plots=self.interactive_plots,
            logger=self.logger,
        )
        save_boxplot(
            df=self.df_normalized,
            output_folder=self.output_folder,
            file_name="normalized_boxplot",
            interactive_plots=self.interactive_plots,
        )
        save_histogram(
            df=self.df_numeric,
            output_folder=self.output_folder,
            interactive_plots=self.interactive_plots,
            logger=self.logger,
        )

        save_corr_matrix(
            df=self.df_numeric,
            output_folder=self.output_folder,
            interactive_plots=self.interactive_plots,
            logger=self.logger,
        )
