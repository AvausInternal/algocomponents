import pytest
from algocomponents.adapters import BigQueryAdapter
import pandas as pd


class TestBigQueryAdapterWithSpacesInColumnNames:
    @pytest.fixture(autouse=True)
    def mock_bigquery_adapter(self, mocker):
        adapter = BigQueryAdapter()
        mocker.patch.object(adapter, "connect", return_value=None)
        return adapter

    def test_df_with_spaces_in_column_names_fails(self, mock_bigquery_adapter):
        df = pd.DataFrame(
            {"column with spaces": [1, 2], "column_without_spaces": [3, 4]}
        )
        with pytest.raises(ValueError) as excinfo:
            mock_bigquery_adapter.connect()
            mock_bigquery_adapter.pandas_df_helper_method(
                df, "test_table", "WRITE_TRUNCATE"
            )
        assert "Spaces aren't allowed in column names in BigQuery" in str(excinfo.value)
