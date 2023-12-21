from configparser import ConfigParser

import numpy as np
import pandas as pd
import pytest

from algocomponents.utils import config_to_str
from algocomponents.utils import predict_with_model


class FakeModel:
    def predict(self, df):
        return [1 for _ in range(len(df))]

    def predict_proba(self, df):
        return np.array([[0.1, 0.9] for _ in range(len(df))])


class TestUtils:
    def test_config_to_str_empty_config(self):
        config = ConfigParser()
        config_str = config_to_str(config)
        assert config_str == "{'DEFAULT': {}}"

    def test_config_to_str_one_section(self):
        config = ConfigParser()
        config.set(section="DEFAULT", option="a", value="b")
        config.set(section="DEFAULT", option="x", value="y")
        config_str = config_to_str(config)
        assert config_str == "{'DEFAULT': {'a': 'b', 'x': 'y'}}"

    def test_config_to_str_two_sections(self):
        config = ConfigParser()
        config.set(section="DEFAULT", option="a", value="b")
        config.set(section="DEFAULT", option="x", value="y")
        config.add_section("DEVIANT")
        config.set(section="DEVIANT", option="a", value="o")
        config.set(section="DEVIANT", option="p", value="q")
        config_str = config_to_str(config)
        assert (
            config_str
            == "{'DEFAULT': {'a': 'b', 'x': 'y'}, 'DEVIANT': {'a': 'o', 'p': 'q', 'x': 'y'}}"
        )

    @pytest.fixture
    def sample_data(self):
        return {
            "metadata": {"model_file": "model.pkl"},
            "df": pd.DataFrame({"feature1": [1, 2, 3], "feature2": [4, 5, 6]}),
            "model_path": "/path/to/model",
        }

    @pytest.fixture(autouse=True)
    def mock_model(self, monkeypatch):
        monkeypatch.setattr("joblib.load", lambda filename: FakeModel())

    def test_predict_with_probabilities(self, sample_data):
        result_df = predict_with_model(
            sample_data["model_path"],
            sample_data["metadata"],
            sample_data["df"].copy(),
            predict_probabilities=True,
        )
        assert "score" in result_df.columns
        assert result_df["score"].tolist() == [0.9, 0.9, 0.9]

    def test_predict_without_probabilities(self, sample_data):
        result_df = predict_with_model(
            sample_data["model_path"],
            sample_data["metadata"],
            sample_data["df"].copy(),
            predict_probabilities=False,
        )
        assert "score" in result_df.columns
        assert result_df["score"].tolist() == [1, 1, 1]
