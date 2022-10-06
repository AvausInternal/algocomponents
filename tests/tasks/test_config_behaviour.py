import os
from configparser import ConfigParser
from unittest import TestCase

from algocomponents.tasks import Task, GroupTask


# Need to define classes here so that it reads the config/config.ini-file
class EmptyTask(Task):
    pass


class EmptyGroupTask(GroupTask):
    pass


class TestConfigBehaviour(TestCase):

    test_config_global_dir = os.path.join("tests", "tasks", "dummy_global_config")
    test_config_local_dir = "dummy_local_config"

    def test_that_config_files_are_parsed(self):
        task = EmptyTask(
            global_config_dir=self.test_config_global_dir,
            local_config_dir="",
        )
        assert task.config["DEFAULT"]["artform"] == "Cinema"
        assert task.config["DEFAULT"]["name"] == "Roundhay Garden Scene"
        assert task.config["DEFAULT"]["year"] == "1888"

    def test_that_local_config_overwrites_global(self):
        task = EmptyTask(
            global_config_dir=self.test_config_global_dir,
            local_config_dir=self.test_config_local_dir,
        )
        assert task.config["DEFAULT"]["artform"] == "Cinema"
        assert task.config["DEFAULT"]["name"] == "Tron"
        assert task.config["DEFAULT"]["year"] == "1982"
        assert task.config["DEREZZED"]["artform"] == "Cinema"
        assert task.config["DEREZZED"]["name"] == "Tron"
        assert task.config["DEREZZED"]["year"] == "2010"

    def test_that_passed_config_overwrites(self):
        config = ConfigParser()

        config.add_section("DEREZZED")
        config.set(section="DEREZZED", option="name", value="Tron Legacy")

        task = EmptyTask(
            global_config_dir=self.test_config_global_dir,
            local_config_dir=self.test_config_local_dir,
            config=config,
        )
        assert task.config["DEFAULT"]["name"] == "Tron"
        assert task.config["DEFAULT"]["year"] == "1982"
        assert task.config["DEREZZED"]["name"] == "Tron Legacy"
        assert task.config["DEREZZED"]["year"] == "2010"

    def test_that_add_to_config_has_highest_priority(self):
        task = EmptyTask(
            global_config_dir=self.test_config_global_dir,
            local_config_dir=self.test_config_local_dir,
        )
        task.add_to_config("name", "TRON")
        assert task.config["DEFAULT"]["name"] == "TRON"

    def test_that_empty_sections_are_populated(self):
        task = EmptyTask(
            global_config_dir=self.test_config_global_dir,
            local_config_dir=self.test_config_local_dir,
        )
        task.add_to_config("name", "TRON")
        assert task.config["DEREZZED"]["name"] == "TRON"

    def test_that_other_sections_are_not_overwritten(self):
        config = ConfigParser()
        config.add_section("DEREZZED")
        config.set(section="DEREZZED", option="name", value="Tron Legacy")

        task = EmptyTask(
            global_config_dir=self.test_config_global_dir,
            local_config_dir=self.test_config_local_dir,
            config=config,
        )
        task.add_to_config("name", "TRON")

        assert task.config["DEFAULT"]["name"] == "TRON"
        assert task.config["DEREZZED"]["name"] == "Tron Legacy"

    def test_overwriting_to_inherited_value_works(self):
        task = EmptyTask(
            global_config_dir=self.test_config_global_dir,
            local_config_dir=self.test_config_local_dir,
            section="DEREZZED",
        )
        task.add_to_config("name", "Tron Legacy")

        assert task.config["DEFAULT"]["name"] == "Tron"
        assert task.config["DEREZZED"]["name"] == "Tron Legacy"

    def test_that_changed_section_is_overwritten(self):
        config = ConfigParser()
        config.add_section("DEREZZED")
        config.set(section="DEREZZED", option="name", value="Tron Legacy")

        task = EmptyTask(
            global_config_dir=self.test_config_global_dir,
            local_config_dir=self.test_config_local_dir,
            config=config,
            section="DEREZZED",
        )
        task.add_to_config("name", "TRON: Legacy")

        assert task.config["DEFAULT"]["name"] == "Tron"
        assert task.config["DEREZZED"]["name"] == "TRON: Legacy"

    def test_that_group_task_propagates_its_config(self):
        task = EmptyTask(
            global_config_dir="",
            local_config_dir="",
        )
        group_task = EmptyGroupTask(
            global_config_dir=self.test_config_global_dir,
            local_config_dir=self.test_config_local_dir,
            task_list=[task],
        )

        assert task.config["DEFAULT"]["artform"] == "Cinema"
        assert task.config["DEFAULT"]["name"] == "Tron"
        assert task.config["DEFAULT"]["year"] == "1982"
        assert task.config["DEREZZED"]["artform"] == "Cinema"
        assert task.config["DEREZZED"]["name"] == "Tron"
        assert task.config["DEREZZED"]["year"] == "2010"

    def test_that_group_task_propagates_its_config_without_overwriting(self):
        task = EmptyTask(
            global_config_dir="",
            local_config_dir=self.test_config_local_dir,
        )
        assert "artform" not in task.config["DEFAULT"]
        assert task.config["DEFAULT"]["name"] == "Tron"
        assert task.config["DEFAULT"]["year"] == "1982"

        group_task = EmptyGroupTask(
            global_config_dir=self.test_config_global_dir,
            local_config_dir="",
            task_list=[task],
        )

        assert group_task.config["DEFAULT"]["artform"] == "Cinema"
        assert group_task.config["DEFAULT"]["name"] == "Roundhay Garden Scene"
        assert group_task.config["DEFAULT"]["year"] == "1888"

        assert task.config["DEFAULT"]["artform"] == "Cinema"
        assert task.config["DEFAULT"]["name"] == "Tron"
        assert task.config["DEFAULT"]["year"] == "1982"
