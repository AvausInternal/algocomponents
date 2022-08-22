from unittest import TestCase

from algocomponents.tasks import Task
from configparser import ConfigParser


# Need to define class here so that it reads the config/config.ini-file
class EmptyTask(Task):
    pass


class TestConfigBehaviour(TestCase):
    def test_that_config_files_are_parsed(self):
        task = EmptyTask()
        assert task.config["DEFAULT"]["name"] == "Tron"
        assert task.config["DEFAULT"]["year"] == "1982"
        assert task.config["DEREZZED"]["name"] == "Tron"
        assert task.config["DEREZZED"]["year"] == "2010"

    def test_that_passed_config_overwrites(self):
        config = ConfigParser()

        config.add_section("DEREZZED")
        config.set(section="DEREZZED", option="name", value="Tron Legacy")

        task = EmptyTask(config=config)
        assert task.config["DEFAULT"]["name"] == "Tron"
        assert task.config["DEFAULT"]["year"] == "1982"
        assert task.config["DEREZZED"]["name"] == "Tron Legacy"
        assert task.config["DEREZZED"]["year"] == "2010"

    def test_that_add_to_config_has_highest_priority(self):
        task = EmptyTask()
        task.add_to_config("name", "TRON")
        assert task.config["DEFAULT"]["name"] == "TRON"

    def test_that_empty_sections_are_populated(self):
        task = EmptyTask()
        task.add_to_config("name", "TRON")
        assert task.config["DEREZZED"]["name"] == "TRON"

    def test_that_other_sections_are_not_overwritten(self):
        config = ConfigParser()
        config.add_section("DEREZZED")
        config.set(section="DEREZZED", option="name", value="Tron Legacy")

        task = EmptyTask(config=config)
        task.add_to_config("name", "TRON")

        assert task.config["DEFAULT"]["name"] == "TRON"
        assert task.config["DEREZZED"]["name"] == "Tron Legacy"

    def test_overwriting_to_inherited_value_works(self):
        task = EmptyTask(section="DEREZZED")
        task.add_to_config("name", "Tron Legacy")

        assert task.config["DEFAULT"]["name"] == "Tron"
        assert task.config["DEREZZED"]["name"] == "Tron Legacy"

    def test_that_changed_section_is_overwritten(self):
        config = ConfigParser()
        config.add_section("DEREZZED")
        config.set(section="DEREZZED", option="name", value="Tron Legacy")

        task = EmptyTask(config=config, section="DEREZZED")
        task.add_to_config("name", "TRON: Legacy")

        assert task.config["DEFAULT"]["name"] == "Tron"
        assert task.config["DEREZZED"]["name"] == "TRON: Legacy"
