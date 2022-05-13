import logging
import os
import sys


class LoggieDoggie:
    """Instantiates and distributes a logger, available in self.logger

    All classes inheriting this will share a common logger with the same config.
    The logger logs to the file log.log and to the terminal.
    """

    log_file_name = "log.log"
    logger_name = "loggie_doggie"
    logger_format = "%(asctime)s [%(filename)s:%(lineno)d] %(levelname)s: %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    log_levels = {
        "NOTSET": logging.NOTSET,
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
    }

    def __init__(self):
        self.logger = logging.getLogger(self.logger_name)
        if not self.logger.hasHandlers():
            self.logger = self.__init_logger()

    def __init_logger(self):
        # Get the logger, set up the formatter
        logger = logging.getLogger(self.logger_name)
        logger.setLevel(level=logging.INFO)
        formatter = logging.Formatter(self.logger_format, self.date_format)

        # Create handler for file output
        file_handler = logging.FileHandler(filename=self.log_file_name)
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)

        logger.addHandler(file_handler)

        # Create handler for terminal output
        terminal_handler = logging.StreamHandler(sys.stdout)
        terminal_handler.setLevel(logging.INFO)
        terminal_handler.setFormatter(formatter)

        logger.addHandler(terminal_handler)

        return logger

    def set_log_level(self, log_level: int):
        logger = logging.getLogger(self.logger_name)
        logger.setLevel(level=log_level)
