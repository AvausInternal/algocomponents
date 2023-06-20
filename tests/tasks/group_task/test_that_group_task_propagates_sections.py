from configparser import ConfigParser
from unittest import TestCase

from algocomponents.tasks import GroupTask, Task


class TestThatGroupTaskPropagatesSections(TestCase):
    test_section = "test"
    another_section = "another"
    config = ConfigParser()
    config.add_section(test_section)
    config.add_section(another_section)

    def test_that_a_task_has_the_section_given_to_it(self):
        task = Task(config=self.config, section=self.test_section)
        assert task.section == self.test_section

    def test_that_a_group_task_propagates_its_section(self):
        task = Task(config=self.config)
        group_task = GroupTask(
            config=self.config, task_list=[task], section=self.test_section
        )
        assert task.section == self.test_section

    def test_that_a_group_task_propagates_its_section_when_none_is_passed(self):
        task = Task(config=self.config, section=None)
        group_task = GroupTask(
            config=self.config, task_list=[task], section=self.test_section
        )
        assert task.section == self.test_section

    def test_that_a_group_task_does_not_overwrite_sections(self):
        task = Task(config=self.config, section=self.test_section)
        group_task = GroupTask(
            config=self.config, task_list=[task], section=self.another_section
        )
        assert task.section == self.test_section

    def test_that_a_group_task_propagates_to_nested_tasks(self):
        task = Task(config=self.config)
        group_task_a = GroupTask(config=self.config, task_list=[task])
        group_task_b = GroupTask(
            config=self.config, task_list=[group_task_a], section=self.test_section
        )
        assert task.section == self.test_section

    def test_that_default_is_overwritten_if_set(self):
        task_a = Task(config=self.config)
        task_b = Task(config=self.config, section=Task._default_section)
        assert task_a.section == Task._default_section
        assert task_b.section == Task._default_section

        group_task = GroupTask(
            config=self.config, task_list=[task_a, task_b], section=self.test_section
        )
        assert task_a.section == self.test_section
        assert task_b.section == Task._default_section

    def test_that_group_task_propagates_correctly_in_complex_structure(self):
        test_section_p = "p"
        test_section_q = "q"
        self.config.add_section(test_section_p)
        self.config.add_section(test_section_q)
        task_a = Task(config=self.config)
        task_b = Task(config=self.config, section=test_section_p)
        task_c = Task(config=self.config)
        task_d = Task(config=self.config, section=test_section_q)
        task_e = Task(config=self.config, section=test_section_p)
        task_f = Task(config=self.config, section=test_section_q)
        group_task_x = GroupTask(config=self.config, task_list=[task_a, task_b])
        group_task_y = GroupTask(
            config=self.config, task_list=[task_c, task_d], section=test_section_p
        )
        group_task_z = GroupTask(
            config=self.config, task_list=[task_e, task_f], section=test_section_q
        )
        group_task = GroupTask(
            config=self.config,
            task_list=[group_task_x, group_task_y, group_task_z],
            section=self.test_section,
        )

        # Task tree for visualization
        # group task, self.test_section
        #   - group_task_x, no adapter
        #       - task_a, no adapter
        #       - task_b, test_section_p
        #   - group_task_y, test_section_p
        #       - task_c, no adapter
        #       - task_d, test_section_q
        #   - group_task_z, test_section_q
        #       - task_e, test_section_p
        #       - task_f, test_section_q

        assert task_a.section == self.test_section
        assert task_b.section == test_section_p
        assert task_c.section == test_section_p
        assert task_d.section == test_section_q
        assert task_e.section == test_section_p
        assert task_f.section == test_section_q
        assert group_task_x.section == self.test_section
        assert group_task_y.section == test_section_p
        assert group_task_z.section == test_section_q
        assert group_task.section == self.test_section
