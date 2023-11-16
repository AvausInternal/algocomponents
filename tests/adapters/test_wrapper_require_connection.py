import pytest

from algocomponents.adapters import LocalSqliteAdapter


class TestWrapperRequireConnection:
    def test_function_requiring_connection_after_connect(self):
        """Test that disconnect can be called after connect without errors."""
        adapter = LocalSqliteAdapter()
        adapter.connect()
        try:
            adapter.table_exists("test")
        except Exception as e:
            pytest.fail(f"Unexpected error occurred: {e}")

    def test_function_requiring_connection_without_connect(self):
        """Test that disconnect without connect raises RuntimeError."""
        adapter = LocalSqliteAdapter()
        with pytest.raises(RuntimeError):
            adapter.table_exists()
