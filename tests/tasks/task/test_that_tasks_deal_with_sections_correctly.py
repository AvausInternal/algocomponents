from configparser import ConfigParser


import pytest

from algocomponents.tasks import Task


class TestThatTasksDealWithSectionsCorrectly:
    nes_section = "NES"
    config = ConfigParser()
    config.add_section(nes_section)

    def test_that_initializing_with_existing_section_works(self):
        task = Task(config=self.config, section=self.nes_section)
        assert task.section == self.nes_section

    def test_that_tasks_use_default_section(self):
        task = Task(config=self.config)
        assert task.section == Task._default_section

    def test_that_section_is_set_works(self):
        task = Task(config=self.config)
        assert not task.section_is_set

        task = Task(config=self.config, section=self.nes_section)
        assert task.section_is_set

        task = Task(config=self.config, section=Task._default_section)
        assert task.section_is_set
        assert task.section == Task._default_section

    def test_that_initializing_with_non_existant_section_returns_error(self):
        with pytest.raises(ValueError):
            Task(config=self.config, section="MEGAMAN")

    def test_that_setting_non_existant_section_returns_error(self):
        with pytest.raises(ValueError):
            task = Task(config=self.config)
            Task(config=self.config).set_section(section="PROTOMAN")
