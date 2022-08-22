from unittest import TestCase

from algocomponents.tasks import Task
from configparser import ConfigParser


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
