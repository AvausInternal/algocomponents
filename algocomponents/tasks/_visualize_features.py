from typing import List

from algocomponents.adapters.custom_exceptions import (
    TableMissingException,
    ColumnMissingException,
)
from algocomponents.tasks import AvausVisuals
from algocomponents.tasks import Task


class VisualizeFeatures(Task):
    """A task that visualizes features in relation to the target label.

    Given an input table, a list of categorical and continuous feature columns
    and the target label, this task will use AvausVisuals to create one
    countplot per categorical feature and one boxplot per continuous feature.

    Attributes:
        input_table: Which table the data to visualize is in.
        target_label_column: Which column in the data is the target label.
        categorical_feature_columns: A list of all the columns that contain
            categorical features that should be plotted.
        continuous_feature_columns: A list of all the columns that contain
            continuous features that should be plotted.
        output_folder: The folder to save the resulting plots in.

    """

    def __init__(
        self,
        input_table: str,
        categorical_feature_columns: List[str],
        continuous_feature_columns: List[str],
        target_label_column: str,
        output_folder: str,
        **kwargs,
    ):
        if len(categorical_feature_columns) != len(set(categorical_feature_columns)):
            raise ValueError(
                f"Received duplicate values for categorical_feature_columns: {categorical_feature_columns}"
            )
        if len(continuous_feature_columns) != len(set(continuous_feature_columns)):
            raise ValueError(
                f"Received duplicate values for continuous_feature_columns: {continuous_feature_columns}"
            )

        super().__init__(**kwargs)
        self.input_table = input_table
        self.target_label_column = target_label_column
        self.categorical_feature_columns = categorical_feature_columns
        self.continuous_feature_columns = continuous_feature_columns
        self.output_folder = output_folder

    def run(self):
        if not self.sql_adapter.table_exists(self.input_table):
            raise TableMissingException(
                f"The input table {self.input_table} does not exist"
            )

        input_table_columns = self.sql_adapter.get_table_columns(self.input_table)
        if not set(self.categorical_feature_columns).issubset(input_table_columns):
            raise ColumnMissingException(
                f"At least one of the columns given as categorical_feature_columns does not exist in the table {self.input_table}.\n"
                f"input_table_columns: {input_table_columns}\n"
                f"categorical_feature_columns: {self.categorical_feature_columns}"
            )
        if not set(self.continuous_feature_columns).issubset(input_table_columns):
            raise ColumnMissingException(
                f"At least one of the columns given as continuous_feature_columns does not exist in the table {self.input_table}.\n"
                f"input_table_columns: {input_table_columns}\n"
                f"continuous_feature_columns: {self.continuous_feature_columns}"
            )

        plotter = AvausVisuals()
        df = self.sql_adapter.table_as_pandas_df(self.input_table)

        for col in self.categorical_feature_columns:
            plotter.countplot(
                x_col=self.target_label_column,
                y_col=col,
                df=df,
                legend=False,
                title=col,
                show=False,
                output_folder=self.output_folder,
                file_name=col,
            )
        for col in self.continuous_feature_columns:
            plotter.boxplot(
                x_col=self.target_label_column,
                y_col=col,
                df=df,
                legend=False,
                title=col,
                show=False,
                output_folder=self.output_folder,
                file_name=col,
            )
