from unittest import TestCase

import pytest

from algocomponents.adapters import LocalSqliteAdapter


class TestThatSQLAdaptersConnectAndDisconnectCorrectly(TestCase):

    sql_adapter = LocalSqliteAdapter()
    format_variables = {
        "TMP_DB": "tmp",
        "OUTPUT_TABLE": "{TMP_DB}.output_table",
    }

    def test_that_format_works_in_base_case(self):
        query = "SELECT 1"
        query_formatted = self.sql_adapter._format_query(
            query=query, format_variables=self.format_variables
        )
        assert query == query_formatted

    def test_that_format_can_replace_variables(self):
        query = "SELECT a FROM {TMP_DB}.test"
        query_formatted = self.sql_adapter._format_query(
            query=query, format_variables=self.format_variables
        )
        assert query_formatted == "SELECT a FROM tmp.test"

    def test_that_format_works_in_nested_formatted_variables(self):
        query = "SELECT a FROM {OUTPUT_TABLE}"
        query_formatted = self.sql_adapter._format_query(
            query=query, format_variables=self.format_variables
        )
        assert query_formatted == "SELECT a FROM tmp.output_table"

    def test_that_error_is_raised_on_recursive_reformatting(self):
        recursive_format_variables = {
            "TMP_DB": "{OUTPUT_TABLE}",
            "OUTPUT_TABLE": "{TMP_DB}.output_table",
        }
        query = "SELECT a FROM {OUTPUT_TABLE}"

        with pytest.raises(RecursionError):
            self.sql_adapter._format_query(
                query=query, format_variables=recursive_format_variables
            )
