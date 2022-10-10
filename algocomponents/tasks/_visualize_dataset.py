import pandas as pd
import numpy as np


from algocomponents.tasks import AdapterTask, SQLTask
from algocomponents.utils import save_boxplot, save_histogram


class VisualizeDataset(AdapterTask):
    """A task that visualizes features
    given a dataset table"""

    def __init__(
        self,
        input_df: pd.DataFrame = None,
        input_csv_file: str = None,
        input_table_name: str = None,
        output_folder: str = "",
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.input_df = input_df
        self.input_csv_file = input_csv_file
        self.input_table_name = input_table_name
        if output_folder == "" or output_folder[-1] == "/":
            self.output_folder = output_folder
        else:
            self.output_folder = output_folder + "/"

        if (
            self.input_csv_file is None
            and self.input_table_name is None
            and self.input_df is None
        ):
            raise ValueError(
                "VisualizeDataset Must get either input_csv_file or input_table_name or input_df,"
                " got neither."
            )

        only_one_true_list = [
            self.input_csv_file is not None,
            self.input_table_name is not None,
            self.input_df is not None,
        ]
        if only_one_true_list.count(True) != 1:
            raise ValueError(
                "VisualizeDataset Must get only one dataset source: input_csv_file or input_table_name or input_df, "
                "got more. "
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

        save_boxplot(df=self.df_numeric, output_folder=self.output_folder)
        save_boxplot(
            df=self.df_normalized,
            output_folder=self.output_folder,
            file_name="normalized_boxplot",
        )
        save_histogram(df=self.df_numeric, output_folder=self.output_folder)
