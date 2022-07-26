from configparser import ConfigParser
from unittest import TestCase
import pandas as pd
import os
import csv

from algocomponents.adapters import LocalSqliteAdapter
from algocomponents.tasks import SQLTask


class TestLocalSqliteAdapterCSVPandas(TestCase):

    sqlite_adapter = LocalSqliteAdapter()

    pandas_query = """SELECT 
            1 AS first, 
            2 AS second, 
            3 AS third
            """
    column_names = ["first", "second", "third"]

    csv_query = """SELECT "I am a csv file" as what_am_i"""
    dirname = path = os.path.dirname(__file__)
    csv_file_path = os.path.join(dirname, "csv_file.csv")

    def run_pandas_task(self):
        pandas_task = SQLTask(
            sql_adapter=self.sqlite_adapter, sql_string=self.pandas_query
        )
        return pandas_task.start().as_pandas()

    def test_pandas_dataframe_type(self):
        pdf = self.run_pandas_task()
        assert type(pdf) == type(pd.DataFrame())

    def test_pandas_column_names(self):
        pdf = self.run_pandas_task()
        assert pdf.columns.values.tolist() == self.column_names

    def test_create_csv_file(self):
        SQLTask(
            sql_string=self.csv_query,
            sql_adapter=self.sqlite_adapter,
        ).start().to_csv(path=self.csv_file_path)
        assert os.path.exists(self.csv_file_path)
        assert os.path.isfile(self.csv_file_path)

    def test_read_csv_file(self):
        rows = []
        with open(self.csv_file_path, "r") as csv_file:
            csvreader = csv.reader(csv_file)
            header = next(csvreader)
            for row in csvreader:
                rows.append(row)
        assert header[1] == "what_am_i"
        assert rows[0][1] == "I am a csv file"

    def test_remove_files(self):
        os.remove(self.csv_file_path)
        assert not os.path.isfile(self.csv_file_path)
