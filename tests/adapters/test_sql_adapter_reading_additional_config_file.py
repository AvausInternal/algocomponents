from configparser import ConfigParser
from typing import List

import pandas as pd

from algocomponents.adapters import SQLAdapter


class BillyMays(SQLAdapter):
    """Technically Ron Popeil was first, but only nerds care about that"""

    def connect(self):
        pass

    def is_connected(self):
        pass

    def disconnect(self):
        pass

    def table_exists(self, table: str) -> bool:
        pass

    def get_table_columns(self, table: str) -> List[str]:
        pass

    def _run_formatted_query(self, query: str):
        pass

    def _format_table_name(self, table: str):
        pass

    def latest_query_as_pandas(self):
        pass

    def pandas_df_as_table(self, df: pd.DataFrame, table: str, overwrite: bool = False):
        pass

    def insert_pandas_df_into_table(self, df: pd.DataFrame, table: str):
        pass

    def latest_query_as_csv(self, path: str):
        pass

    def count_rows_in_table(self, table: str):
        pass


class TestSQLAdapterReadingAdditionalConfigFile:
    def test_that_adapters_read_their_own_config(self):
        """Tests that adapter can read it's own config"""
        adapter = BillyMays(adapter_config_file="billy_mays_config.ini")

        assert adapter.config["DEFAULT"]["sales_pitch"] == "But wait, there's more!"

    def test_that_adapter_configs_overwrite_non_adapter_config(self):
        """Tests that adapter config overwrite the default configs"""
        adapter = BillyMays(adapter_config_file="billy_mays_config.ini")

        assert adapter.config["DEFAULT"]["tmp_db"] == "not_so_tmp"

    def test_that_adapter_function_without_config_files(self):
        """Tests that adapters work fine without being given a config file"""
        adapter = BillyMays()

        assert adapter.config["DEFAULT"]["tmp_db"] == "tmp"

    def test_that_passed_config_still_takes_priority(self):
        """Tests that passed config takes precedence over adapter config files"""
        special_config = ConfigParser()
        special_config["DEFAULT"]["tmp_db"] = "Literally production"
        adapter = BillyMays(
            adapter_config_file="billy_mays_config.ini",
            config=special_config,
        )

        assert adapter.config["DEFAULT"]["sales_pitch"] == "But wait, there's more!"
        assert adapter.config["DEFAULT"]["tmp_db"] == "Literally production"
