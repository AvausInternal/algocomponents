import pytest

from algocomponents.adapters import LocalSqliteAdapter, BigQueryAdapter
from algocomponents.utils._launch_task import _get_adapter


class TestGetAdapter:
    """Verifies that the _get_adapter function works as intended"""

    def test_with_correct_adapter_name(self):
        sql_adapter = _get_adapter("local_sqlite_adapter")
        assert type(sql_adapter) == LocalSqliteAdapter

    def test_with_adapter_name_that_requires_lower(self):
        sql_adapter = _get_adapter("BigQueryAdapter")
        assert type(sql_adapter) == BigQueryAdapter

    def test_that_adapters_get_sections(self):
        sql_adapter = _get_adapter("SparkAdapter")
        assert sql_adapter.section_is_set is False

        sql_adapter = _get_adapter("DataBricksAdapter", section="DEFAULT")
        assert sql_adapter.section_is_set

    def test_that_value_error_is_raised_on_missing_section(self):
        with pytest.raises(ValueError):
            _get_adapter("SparkAdapter", section="N00B")
