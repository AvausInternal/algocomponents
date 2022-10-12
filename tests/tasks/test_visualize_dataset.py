from unittest import TestCase
import pandas as pd
import os.path

from algocomponents.tasks import VisualizeDataset
from algocomponents.adapters import LocalSqliteAdapter


class TestVisualizeDataset(TestCase):
    """Test VisualizeDataset task class"""

    csv_file_path = "tests/tasks/visualize_dataset_csv/tiny_dataset.csv"
    csv_empty_path = "tests/tasks/visualize_dataset_csv/empty.csv"
    df = pd.read_csv(csv_file_path)
    df_empty = pd.DataFrame()
    gcp_input_table = "{TMP_DB}.tiny_dataset"
    folder = "tests/tasks/visualize_dataset_csv"

    def test_that_error_is_raised_no_dataset_argument(self):
        with self.assertRaises(ValueError):
            VisualizeDataset()

    def test_that_error_is_raised_too_many_dataset_arguments(self):
        with self.assertRaises(ValueError):
            VisualizeDataset(input_df=self.df, input_csv_file=self.csv_file_path)
        with self.assertRaises(ValueError):
            VisualizeDataset(
                input_df=self.df,
                input_table_name=self.gcp_input_table,
                sql_adapter=LocalSqliteAdapter,
            )
        with self.assertRaises(ValueError):
            VisualizeDataset(
                input_csv_file=self.csv_file_path,
                input_table_name=self.gcp_input_table,
                sql_adapter=LocalSqliteAdapter,
            )
        with self.assertRaises(ValueError):
            VisualizeDataset(
                input_df=self.df,
                input_csv_file=self.csv_file_path,
                input_table_name=self.gcp_input_table,
                sql_adapter=LocalSqliteAdapter,
            )

    def test_that_error_is_raised_input_table_without_adapter(self):
        with self.assertRaises(ValueError):
            VisualizeDataset(input_table_name=self.gcp_input_table)

    def test_that_plots_are_properly_saved(self):
        vd_task = VisualizeDataset(input_df=self.df, output_folder=self.folder)
        vd_task.start()
        if self.folder == "" or self.folder[-1] == "/":
            folder_name = self.folder
        else:
            folder_name = self.folder + "/"
        self.assertTrue(os.path.exists(f"{folder_name}boxplot.png"))
        self.assertTrue(os.path.exists(f"{folder_name}normalized_boxplot.png"))
        # should it be extended to histograms and corr as well?

    def test_empty_df(self):
        with self.assertRaises(ValueError):
            VisualizeDataset(input_df=self.df_empty)

    def test_empty_csv_file(self):
        pass

    def test_empty_table(self):
        pass
