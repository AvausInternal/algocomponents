import logging
import sys


class LoggieDoggie:
    """Your loyal LoggieDoggie that fetches loggers

    LoggieDoggie will fetch a logger given a name. If that logger is fetched for
    the first time, the logger will be set up with handlers. If the logger has
    handlers, it will be evaluated as "having already been set up" and returned.
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

    def fetch_logger(
        self,
        logger_name: str,
        log_level: str = "INFO",
        log_to_file: bool = True
    ):
        logger = logging.getLogger(logger_name)
        if logger.hasHandlers():
            return logger

        # Get the logger, set up the formatter
        logger = logging.getLogger(logger_name)
        logger.setLevel(level=logging.INFO)
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

        if log_level not in self.log_levels.keys():
            raise AttributeError(
                f"Tried to set log level to {log_level} which is not in {list(self.log_levels.keys())}"
            )
        logger.setLevel(level=log_level)

        return logger
