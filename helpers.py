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
