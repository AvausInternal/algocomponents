from unittest import TestCase

import pytest

from algocomponents.config_reader import ConfigReader


class TestConfigReaderFormatString(TestCase):
    config_reader = ConfigReader()
    format_variables = {
        "TMP_DB": "tmp",
        "OUTPUT_TABLE": "{TMP_DB}.output_table",
    }

    def test_that_format_works_in_base_case(self):
        query = "SELECT 1"
        query_formatted = self.config_reader.format_string(
            string=query, additional_format_variables=self.format_variables
        )
        assert query == query_formatted

    def test_that_format_can_replace_variables(self):
        query = "SELECT a FROM {TMP_DB}.test"
        query_formatted = self.config_reader.format_string(
            string=query, additional_format_variables=self.format_variables
        )
        assert query_formatted == "SELECT a FROM tmp.test"

    def test_that_format_works_in_nested_formatted_variables(self):
        query = "SELECT a FROM {OUTPUT_TABLE}"
        query_formatted = self.config_reader.format_string(
            string=query, additional_format_variables=self.format_variables
        )
        assert query_formatted == "SELECT a FROM tmp.output_table"

    def test_that_error_is_raised_on_recursive_reformatting(self):
        recursive_format_variables = {
            "TMP_DB": "{OUTPUT_TABLE}",
            "OUTPUT_TABLE": "{TMP_DB}.output_table",
        }
        query = "SELECT a FROM {OUTPUT_TABLE}"

        with pytest.raises(RecursionError):
            self.config_reader.format_string(
                string=query, additional_format_variables=recursive_format_variables
            )
