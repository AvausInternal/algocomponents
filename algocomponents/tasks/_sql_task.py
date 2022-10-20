from algocomponents.tasks import AdapterTask


class SQLTask(AdapterTask):
    """A task used to run SQL queries with an adapter.

    The sql_file_path is the path to the file from the project root.

    Args:
        sql_file_path: Where the sql file to be run is
        sql_string: The sql string to run

    """

    def __init__(
        self,
        sql_file_path: str = None,
        sql_string: str = None,
        **kwargs,
    ):
        super().__init__(**kwargs)

        self.sql_file_path = sql_file_path
        self.sql_string = sql_string

        assert (
            self.sql_file_path or self.sql_string
        ), "SQLTask Must get either sql_file_path or sql_string, got neither."

    def run(self):
        """Runs either the sql_string or the sql_file_path

        If an sql_string is given, this takes priority. If an sql_file_path is
        given, the text inside it is parsed and then run using run_sql_string()

        """
        if self.sql_string:
            self.sql_adapter.run_sql_string(
                sql_string=self.sql_string,
                format_variables=dict(self.config[self.section]),
            )
        elif self.sql_file_path:
            self.sql_adapter.run_sql_file(
                path=self.sql_file_path,
                format_variables=dict(self.config[self.section]),
            )

    def as_pandas(self):
        """Returns the result as a pandas dataframe

        This method is intended for method cascading: task.start().as_pandas()

        """
        return self.sql_adapter.latest_query_as_pandas()

    def to_csv(self, path: str):
        """Returns the result as a csv_file

        This method is intended for method cascading: task.start().to_csv(path)

        """
        self.sql_adapter.latest_query_as_csv(path=path)
