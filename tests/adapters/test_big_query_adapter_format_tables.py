import os
from configparser import ConfigParser

from algocomponents.adapters import BigQueryAdapter, SQLAdapter


class TestBigQueryAdapterFormatTables:
    gcp_project = "avaus-academy"
    config = ConfigParser()
    config.set(section="DEFAULT", option="gcp_project", value=gcp_project)
    big_query_adapter = BigQueryAdapter(config=config)
    big_query_adapter_without_config = BigQueryAdapter()

    def test_big_query_adapter_format_tables(self):
        self.format_queries_in_folder(
            folder="big_query_adapter_format_queries",
            sql_adapter=self.big_query_adapter,
        )

    def test_big_query_adapter_format_tables_without_config(self):
        self.format_queries_in_folder(
            folder="big_query_adapter_format_queries_without_config",
            sql_adapter=self.big_query_adapter_without_config,
        )

    @staticmethod
    def format_queries_in_folder(sql_adapter: SQLAdapter, folder: str):
        folder = os.path.join(os.path.dirname(__file__), folder)
        queries = os.listdir(folder)
        for file in queries:
            with open(os.path.join(folder, file)) as f:
                contents = f.read()
            input_query, correctly_formatted_query = contents.split(";")

            if correctly_formatted_query.strip() == "":
                correctly_formatted_query = input_query

            formatted_query = sql_adapter.get_formatted_queries(
                sql_string=input_query.strip()
            )[0]
            assert formatted_query == correctly_formatted_query.strip()
