
import logging
import sys
from logging import getLevelName

def set_logging_level(logger, logging_level: str):
    if logging_level.upper() in [
        "DEBUG",
        "INFO",
        "WARNING",
        "ERROR",
        "CRITICAL",
    ]:
        return logger.setLevel(getLevelName(logging_level.upper()))
    else:
        return logger.error(f"Logging level {logging_level} not recognized!")


def set_up_logger(logging_level="INFO"):
    #setup logger
    logger = logging.getLogger()
    set_logging_level(logger, logging_level)
    formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s', 
                                '%m-%d-%Y %H:%M:%S')
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(formatter)
    logger.addHandler(stdout_handler)

    return logger 