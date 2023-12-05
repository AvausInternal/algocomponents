import pandas as pd
import pytest

from algocomponents.adapters import LocalSqliteAdapter
from algocomponents.tasks import VisualizeDataset


class TestVisualizeDataset:
    """Test VisualizeDataset task class"""

    csv_file_path = "tests/tasks/visualize_dataset/tiny_dataset.csv"
    csv_empty_path = "tests/tasks/visualize_dataset/empty.csv"
    df = pd.read_csv(csv_file_path)
    df_empty = pd.DataFrame()
    gcp_input_table = "tmp.tiny_dataset"
    folder = "tests/tasks/visualize_dataset"

    def test_that_error_is_raised_no_dataset_argument(self):
        with pytest.raises(ValueError):
            VisualizeDataset()

    def test_that_error_is_raised_too_many_dataset_arguments(self):
        with pytest.raises(ValueError):
            VisualizeDataset(input_df=self.df, input_csv_file=self.csv_file_path)
        with pytest.raises(ValueError):
            VisualizeDataset(
                input_df=self.df,
                input_table_name=self.gcp_input_table,
                sql_adapter=LocalSqliteAdapter,
            )
        with pytest.raises(ValueError):
            VisualizeDataset(
                input_csv_file=self.csv_file_path,
                input_table_name=self.gcp_input_table,
                sql_adapter=LocalSqliteAdapter,
            )
        with pytest.raises(ValueError):
            VisualizeDataset(
                input_df=self.df,
                input_csv_file=self.csv_file_path,
                input_table_name=self.gcp_input_table,
                sql_adapter=LocalSqliteAdapter,
            )

    def test_that_error_is_raised_input_table_without_adapter(self):
        with pytest.raises(ValueError):
            VisualizeDataset(input_table_name=self.gcp_input_table)

    def test_empty_df(self):
        with pytest.raises(ValueError):
            VisualizeDataset(input_df=self.df_empty)

    def test_empty_csv_file(self):
        with pytest.raises(pd.errors.EmptyDataError):
            vd_task = VisualizeDataset(input_csv_file=self.csv_empty_path)
            vd_task.start()
