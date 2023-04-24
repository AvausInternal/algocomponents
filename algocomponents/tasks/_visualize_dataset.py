from typing import List

import pandas as pd

from algocomponents.tasks import Task
from algocomponents.utils import save_boxplot, save_histogram, save_corr_matrix


class VisualizeDataset(Task):
    """A task that visualizes features given a dataset table.

    The task takes one of the following dataset sources as input:
    input_df, input_csv_file or input_table_name and save descriptive plots:
    boxplot, normalized boxplot, histograms, correlation matrix of that dataset.

    Attributes:
        input_df: Pandas DataFrame with dataset to visualize.
        input_csv_file: Csv file path with dataset to visualize.
        input_table_name: Database table name with dataset to visualize
            following "{DATASET}.{TABLE}" naming convention.
        continuous_features: A list of all continuous features to plot
        categorical_features: A list of all categorical features to plot
        excluded_columns: A list of columns to not plot
        find_feature_columns: A boolean flag indicating whether this task should
            attempt to find the columns on its own. Cannot be set to True if
            either continuous_features or categorical_features are set
        output_folder (str, optional): Folder name or folder path, where plots are to be saved.
        interactive_plots (bool, optional): Whether to additionally save interactive plots.

    """

    def __init__(
        self,
        input_df: pd.DataFrame = None,
        input_csv_file: str = None,
        input_table_name: str = None,
        continuous_features: List[str] = None,
        categorical_features: List[str] = None,
        excluded_columns: List[str] = None,
        find_feature_columns: bool = False,
        output_folder: str = "",
        interactive_plots: bool = True,
        **kwargs,
    ):
        if find_feature_columns:
            if continuous_features or categorical_features:
                raise ValueError(
                    "When running with find_feature_columns as True,"
                    "you cannot specify continuous_features or categorical_features."
                )

        only_one_true_list = [
            input_csv_file is not None,
            input_table_name is not None,
            input_df is not None,
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

        if input_df is not None and input_df.empty:
            raise ValueError("Input_df is empty.")

        super().__init__(**kwargs)
        if input_table_name and self.sql_adapter is None:
            raise ValueError("You must provide sql_adapter with input_table_name.")

        self.input_df = input_df
        self.input_csv_file = input_csv_file
        self.input_table_name = input_table_name
        self.continuous_features = continuous_features or []
        self.categorical_features = categorical_features or []
        self.excluded_columns = excluded_columns or []
        self.output_folder = output_folder
        self.interactive_plots = interactive_plots
        self.find_feature_columns = find_feature_columns

    def run(self):
        if self.input_csv_file:
            self.input_df = pd.read_csv(f"{self.input_csv_file}")
        elif self.input_table_name:
            self.input_df = self.sql_adapter.table_as_pandas_df(self.input_table_name)

        if self.find_feature_columns:
            numerics = ["int16", "int32", "int64", "float16", "float32", "float64"]
        else:
            numerics = self.continuous_features

        self.df_numeric = self.input_df.select_dtypes(include=numerics)
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
            df=self.input_df,
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
