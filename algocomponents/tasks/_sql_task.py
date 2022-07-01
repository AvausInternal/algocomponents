from configparser import ConfigParser

from algocomponents.adapters import SQLAdapter, LocalSqliteAdapter
from algocomponents.tasks import AdapterTask


class SQLTask(AdapterTask):
    """A task used to run SQL queries with an adapter.

    The sql_file_path is the path to the file from the project root.
    """

    def __init__(
        self,
        sql_file_path: str = None,
        sql_string: str = None,
        sql_adapter: SQLAdapter = None,
        config: ConfigParser = None,
        section: str = None,
    ):
        super().__init__(
            sql_adapter=sql_adapter,
            config=config,
            section=section,
        )

        self.sql_file_path = sql_file_path
        self.sql_string = sql_string

        assert (
            self.sql_file_path or self.sql_string
        ), "SQLTask Must get either sql_file_path or sql_string, got neither."

    def run(self):
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
