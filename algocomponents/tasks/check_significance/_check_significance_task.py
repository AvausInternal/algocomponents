import os

from algocomponents.adapters.custom_exceptions import (
    TableMissingException,
    ColumnMissingException,
)
from algocomponents.tasks import Task
from algocomponents.utils import ABTools


class CheckSignificanceTask(Task):
    """Task that checks whether a test results were statistically significant

    This task runs Welch's t-test for every kpi column in the input table.
    The group column must contain values which speficy does the value belong
    to the test or control group. The results are logged for every t-test.

    Args:
        input_table: Table which contains the data.
        group_column: Name of the columnn which specifies the groups.
        kpi_columns: List of column names for which the test is performed.
        group_names: List specifying what the group names are.
        sig_level: Significance level often denoted as alpha, typically 0.05.
        tail: `one_sided` or `two_sided` test.

    """

    _default_group_names = ["test", "control"]

    def __init__(
        self,
        input_table: str,
        group_column: str,
        kpi_columns: list,
        group_names: list = None,
        sig_level: float = ABTools._default_significance_level,
        tail: str = ABTools._default_tail,
        **kwargs,
    ):
        super().__init__(**kwargs)

        self.input_table = input_table
        self.group_column = group_column
        self.kpi_columns = kpi_columns
        self.sig_level = sig_level
        self.tail = tail
        self.group_names = group_names or self._default_group_names

        self.ab_tools = ABTools()
        self.sql_folder = os.path.join(self.classpath, "sql")
        self.format_variables = {
            "input_table": self.input_table,
            "group_column": self.group_column,
        }

    def run(self):
        self.sql_adapter.connect()

        # check that the input table exists
        if not self.sql_adapter.table_exists(self.input_table):
            self.sql_adapter.disconnect()
            raise TableMissingException(
                f"Input table: {self.input_table} doesn't exist"
            )

        # check that the input table contains all the columns
        input_table_columns = self.sql_adapter.get_table_columns(self.input_table)
        for column in self.kpi_columns + [self.group_column]:
            if not column in input_table_columns:
                self.sql_adapter.disconnect()
                raise ColumnMissingException(
                    f"Column {column} is missing from the table {self.input_table}"
                )

        # check that there are only 2 groups
        assert (
            len(self.group_names) == 2
        ), f"You gave {len(self.group_names)} groups but only 2 groups is supported"

        # test significance for all kpi columns
        for target_column in self.kpi_columns:
            self.format_variables["target_column"] = target_column
            data = {}

            # get mean, variance and size for test group and control group
            for group in self.group_names:
                self.format_variables["group_"] = group
                data[group] = {}

                # sql files are in this order: size, average, variance
                for file in os.listdir(self.sql_folder):
                    sql_file = os.path.join(self.sql_folder, file)
                    df = self.sql_adapter.run_sql_file(
                        path=sql_file, format_variables=self.format_variables
                    )[0]
                    data[group][file.replace(".sql", "")] = df.values[0][0]

            self.ab_tools.logger.info(f"Significance test for: {target_column}")
            (t, p_val) = self.ab_tools.is_significant_continuous(
                n1=data[self.group_names[0]]["size"],
                n2=data[self.group_names[1]]["size"],
                x1=data[self.group_names[0]]["average"],
                x2=data[self.group_names[1]]["average"],
                var1=data[self.group_names[0]]["variance"],
                var2=data[self.group_names[1]]["variance"],
                sig_level=self.sig_level,
                tail=self.tail,
            )
