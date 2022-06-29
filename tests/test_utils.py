from configparser import ConfigParser
from unittest import TestCase

from algocomponents.utils import config_to_str


class TestUtils(TestCase):

    def test_config_to_str_empty_config(self):
        config = ConfigParser()
        config_str = config_to_str(config)
        assert (config_str == "{'DEFAULT': {}}")

    def test_config_to_str_one_section(self):
        config = ConfigParser()
        config.set(section="DEFAULT", option="a", value="b")
        config.set(section="DEFAULT", option="x", value="y")
        config_str = config_to_str(config)
        assert (config_str == "{'DEFAULT': {'a': 'b', 'x': 'y'}}")

    def test_config_to_str_two_sections(self):
        config = ConfigParser()
        config.set(section="DEFAULT", option="a", value="b")
        config.set(section="DEFAULT", option="x", value="y")
        config.add_section("DEVIANT")
        config.set(section="DEVIANT", option="a", value="o")
        config.set(section="DEVIANT", option="p", value="q")
        config_str = config_to_str(config)
        assert (config_str == "{'DEFAULT': {'a': 'b', 'x': 'y'}, 'DEVIANT': {'a': 'o', 'p': 'q', 'x': 'y'}}")
