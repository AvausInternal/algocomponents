import os.path
from unittest import TestCase

import pandas as pd

from algocomponents.utils import save_boxplot, save_histogram, save_corr_matrix


class TestSavePlots(TestCase):
    """Test save plots utility functions"""

    csv_file_path = "tests/tasks/visualize_dataset/tiny_dataset.csv"
    input_df = pd.read_csv(csv_file_path)
    numerics = ["int16", "int32", "int64", "float16", "float32", "float64"]
    df_numeric = input_df.select_dtypes(include=numerics)
    folder = "tests/tasks/visualize_dataset"

    def test_saving_boxplot_interactive_false(self):
        save_boxplot(
            df=self.df_numeric, output_folder=self.folder, interactive_plots=False
        )

        self.assertTrue(os.path.exists(os.path.join(self.folder, "boxplot.png")))
        self.assertFalse(os.path.exists(os.path.join(self.folder, "boxplot.html")))

    def test_saving_boxplot_interactive_name_changed(self):
        save_boxplot(
            df=self.df_numeric, output_folder=self.folder, file_name="boxplot2", open_interactive_plot=False,
        )

        self.assertTrue(os.path.exists(os.path.join(self.folder, "boxplot2.png")))
        self.assertTrue(os.path.exists(os.path.join(self.folder, "boxplot2.html")))

    def test_saving_corr_matrix_interactive_false(self):
        save_corr_matrix(
            df=self.df_numeric, output_folder=self.folder, interactive_plots=False
        )

        self.assertTrue(os.path.exists(os.path.join(self.folder, "corr_matrix.png")))
        self.assertFalse(os.path.exists(os.path.join(self.folder, "corr_matrix.html")))

    def test_saving_corr_matrix_interactive_name_changed(self):
        save_corr_matrix(
            df=self.df_numeric, output_folder=self.folder, file_name="corr_matrix2", open_interactive_plot=False,
        )

        self.assertTrue(os.path.exists(os.path.join(self.folder, "corr_matrix2.png")))
        self.assertTrue(os.path.exists(os.path.join(self.folder, "corr_matrix2.html")))

    def test_saving_histograms_interactive_false(self):
        save_histogram(
            df=self.input_df, output_folder=self.folder, interactive_plots=False
        )

        for col in self.input_df:
            self.assertTrue(
                os.path.exists(os.path.join(self.folder, f"histogram-{col}.png"))
            )
            self.assertFalse(
                os.path.exists(os.path.join(self.folder, f"histogram-{col}.html"))
            )

    def test_saving_histograms_interactive_name_changed(self):
        save_histogram(
            df=self.input_df, output_folder=self.folder, file_name="histogram2", open_interactive_plot=False,
        )

        for col in self.input_df:
            self.assertTrue(
                os.path.exists(os.path.join(self.folder, f"histogram2-{col}.png"))
            )
            self.assertTrue(
                os.path.exists(os.path.join(self.folder, f"histogram2-{col}.html"))
            )

    def tearDown(self):
        my_dir = self.folder
        for file_name in os.listdir(my_dir):
            if file_name.startswith(("boxplot", "corr_matrix", "histogram")):
                os.remove(os.path.join(my_dir, file_name))
