from unittest import TestCase
import pandas as pd
import os.path

from algocomponents.tasks import VisualizeDataset
from algocomponents.adapters import LocalSqliteAdapter
from algocomponents.tasks import AvausVisuals


class TestAvausVisuals(TestCase):
    """Test AvausVisuals class"""

    output_path = os.path.join("tests", "tasks", "avaus_visuals")
    df_to_plot = pd.DataFrame(
        data={
            "x": [0],
            "y": [0],
        }
    )
    plotter = AvausVisuals()

    def test_saving_a_lineplot(self):
        self.plotter.boxplot(
            df=self.df_to_plot,
            x_col="x",
            y_col="y",
            show=False,
            file_name="test_saving_a_lineplot",
            output_folder=self.output_path,
        )
        output_file = os.path.join(self.output_path, "test_saving_a_lineplot.png")
        assert os.path.isfile(output_file)
        os.remove(output_file)

    def test_saving_a_boxplot(self):
        self.plotter.boxplot(
            df=self.df_to_plot,
            x_col="x",
            y_col="y",
            show=False,
            file_name="test_saving_a_boxplot",
            output_folder=self.output_path,
        )
        output_file = os.path.join(self.output_path, "test_saving_a_boxplot.png")
        assert os.path.isfile(output_file)
        os.remove(output_file)

    def test_saving_a_countplot(self):
        self.plotter.countplot(
            df=self.df_to_plot,
            x_col="x",
            y_col="y",
            show=False,
            file_name="test_saving_a_countplot",
            output_folder=self.output_path,
        )
        output_file = os.path.join(self.output_path, "test_saving_a_countplot.png")
        assert os.path.isfile(output_file)
        os.remove(output_file)

    def test_saving_to_missing_directory(self):
        deep_path = os.path.join(self.output_path, "new_directory")
        self.plotter.countplot(
            df=self.df_to_plot,
            x_col="x",
            y_col="y",
            show=False,
            file_name="test_saving_in_new_dir",
            output_folder=deep_path,
        )
        output_file = os.path.join(deep_path, "test_saving_in_new_dir.png")
        assert os.path.isfile(output_file)
        os.remove(output_file)
        os.removedirs(deep_path)
