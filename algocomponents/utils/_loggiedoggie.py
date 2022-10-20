import logging
import sys
from typing import Dict


class LoggieDoggie:
    """Your loyal LoggieDoggie that fetches loggers

    LoggieDoggie will fetch a logger given a name. If that logger is fetched for
    the first time, the logger will be set up with handlers. If the logger has
    handlers, it will be evaluated as "having already been set up" and returned.

    Properties:
        log_file_name: Name of log file to create or append to
        logger_format: How log messages will be formatted
        date_format: The format to use for the date in the log format
        log_levels: Allowed log_levels

        _default_log_level: Log level to use when no log level is given
        _default_log_to_file: Whether to log to file or not when setting is not present in config

    """

    log_file_name = "log.log"
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

    _default_log_level = "INFO"
    _default_log_to_file = True

    def fetch_logger(
        self,
        logger_name: str,
        config: Dict = None,
    ):
        """Fetch a logger by logger name, or create one if one did not exist

        Args:
            logger_name: Name of the logger to either create or fetch
            config: A dictionary of settings, out of which these are read:
                log_level: At what level to log
                log_to_file: Whether log should also output to file

        """
        if not config:
            config = {}

        # Read log_level from config
        if "log_level" in config.keys():
            log_level = config["log_level"]
        else:
            log_level = self._default_log_level

        if log_level not in self.log_levels.keys():
            raise AttributeError(
                f"Tried to set log level to {log_level} which is not in {list(self.log_levels.keys())}"
            )

        # Read log_to_file from config
        if "log_to_file" in config.keys():
            if config["log_to_file"].lower() in ["true", "t", "1", "y"]:
                log_to_file = True
            elif config["log_to_file"].lower() in ["false", "f", "0", "n"]:
                log_to_file = False
            else:
                raise AttributeError(
                    f"log_to_file cannot be parsed to bool value: {config['log_to_file']}"
                )
        else:
            log_to_file = self._default_log_to_file

        # Construct a unique log name based on logger name and config
        unique_logger_name = f"{logger_name}_{log_level}_{log_to_file}"

        logger = logging.getLogger(unique_logger_name)
        if logger.hasHandlers():
            return logger

        # Get the logger, set up the formatter
        logger.setLevel(level=log_level)
        formatter = logging.Formatter(self.logger_format, self.date_format)

        if log_to_file:
            # Create handler for file output
            file_handler = logging.FileHandler(filename=self.log_file_name)
            file_handler.setLevel(logging.NOTSET)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

        # Create handler for terminal output
        terminal_handler = logging.StreamHandler(sys.stdout)
        terminal_handler.setLevel(logging.NOTSET)
        terminal_handler.setFormatter(formatter)

        logger.addHandler(terminal_handler)

        return logger
