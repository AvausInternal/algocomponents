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
        if output_folder == "":
            self.output_folder = output_folder
        else:
            self.output_folder = output_folder + "/"

        assert (
            self.input_csv_file or self.input_table_name or (self.input_df is not None)
        ), "VisualizeDataset Must get either input_csv_file or input_table_name or input_df, got neither."

        if self.input_table_name:
            assert (
                self.sql_adapter
            ), "You must provide sql_adapter with input_table_name."

        assert (
            len(
                [
                    1
                    for val in [
                        self.input_csv_file,
                        self.input_table_name,
                        self.input_df,
                    ]
                    if val is not None
                ]
            )
            == 1
        ), "VisualizeDataset Must get only one dataset source (input_csv_file/input_table_name/input_df), got more."

        if self.input_df is not None:
            assert not input_df.empty, "Input_df is empty."

    def run(self):
        if self.input_csv_file:
            self.input_df = pd.read_csv(f"{self.input_csv_file}")
        elif self.input_table_name:
            sql_string = f"SELECT * FROM `{self.input_table_name}`"

            sql_task_df = SQLTask(sql_string=sql_string, sql_adapter=self.sql_adapter)
            self.input_df = sql_task_df.start().as_pandas()

        # dataframe with only numerical features
        self.df_numeric = self.input_df.select_dtypes(include=np.number)
        # dataframe with only numerical features and normalized values
        self.df_normalized = (self.df_numeric - self.df_numeric.min()) / (
            self.df_numeric.max() - self.df_numeric.min()
        )

        save_boxplot(df=self.input_df, output_folder=self.output_folder)
        save_boxplot(
            df=self.df_normalized,
            output_folder=self.output_folder,
            file_name="normalized_boxplot",
        )
        save_histogram(df=self.df_numeric, output_folder=self.output_folder)
