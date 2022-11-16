import uuid
from datetime import datetime

from algocomponents.config_reader import ConfigReader
from algocomponents.utils import config_to_str


class Task(ConfigReader):
    """A generic task which starts using its start()-method.

    The task initiates a logger, finds its classpath (where it is located), and
    parses a config file. The log is written to a file in root called log.log,
    and the config file is read from a folder called config, located where this
    class resides. The config is an ini-file, parsed with pythons ConfigParser.

    Args:
        global_config_dir: Path from project root to global config.ini-file.
        global_config_dir: Relative path to local config.ini-file.
        config: A passed ConfigParser object, which overwrites any files read.
        section: Which section of the ConfigParsers should be read from.

    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.task_name = self.class_name
        self.run_id = None
        self.parent = None

    def start(self):
        """Starts the task

        This is the method to use when starting a task. This method will call
        the three following methods in order:

            startup()
            run()
            shutdown()

        The above methods are the methods other tasks overwrite with their own
        functionality. For a Task, all of these three methods are blank.

        """
        run_start = datetime.now()

        if self.parent:
            self.run_id = self.parent.run_id
        else:
            self.run_id = str(uuid.uuid1())

        self.logger.info(
            f"Starting task {self.task_name} " f"with section {self.section}"
        )
        self.logger.debug(config_to_str(self.config))

        self.startup()
        self.run()
        self.shutdown()

        now = datetime.now()
        self.logger.info(f"Task {self.task_name} finished after {now - run_start}")

        return self

    def startup(self):
        """What the task needs to do before executing it's main functionality"""
        pass

    def run(self):
        """The tasks main functionality"""
        pass

    def shutdown(self):
        """What the task needs to do after executing it's main funcionality"""
        pass
