import os
import re
from abc import ABC
from configparser import ConfigParser

from algocomponents.adapters import SQLAdapter
from algocomponents.tasks import GroupTask, SQLTask


class SQLPipeline(GroupTask, ABC):
    """The SQLPipeline will run all queries in its sql folder as SQLTasks

    Using whichever adapter and config is supplied, the SQLPipeline will go to
    an sql folder expected to be located at the same place as the SQLPipeline
    class, and run all of those queries in order. If no adapter is given, the
    LocalSqliteAdapter will be used. The files in the sql folder must have a
    specific format: 1_example.sql, 2_second_example.sql, etc
    """

    sql_file_pattern = "[0-9]+_"  # Numeric followed by underscore

    def __init__(
            self,
            sql_folder: str = None,
            sql_adapter: SQLAdapter = None,
            config: ConfigParser = None,
            section: str = None,
    ):
        super().__init__(sql_adapter=sql_adapter, config=config, section=section)

        self.sql_folder = sql_folder or os.path.join(self.classpath, "sql")

        self.task_list = self.get_sql_tasks()

    def get_sql_tasks(self):
        if not os.path.exists(self.sql_folder):
            self.logger.warning(f"Folder does not exist: {self.sql_folder}")
            return []

        sql_files = os.listdir(self.sql_folder)
        regex_pattern = re.compile(self.sql_file_pattern)

        for sql_file in sql_files:
            if not regex_pattern.match(sql_file):
                raise NameError(
                    "SQL files are not numbered, cannot determine order of "
                    f"operations. Expected \"1_example.sql\", found: {sql_file}"
                )

        # Split filename on _, take the first instance, and then sort as if that
        # was an int. ["12_example.sql", "8_example.sql"] -> [12, 8] -> [8, 12]
        sql_files.sort(key=lambda x: int(x.split("_")[0]))

        task_list = []

        for sql_file in sql_files:
            full_path = os.path.join(self.sql_folder, sql_file)
            sql_task = SQLTask(
                sql_file_path=full_path,
                sql_adapter=self.sql_adapter,
                config=self.config,
                section=self.section,
            )
            sql_task.parent = self
            task_list.append(sql_task)

        return task_list
