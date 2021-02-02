import logging
import sys
from logging.handlers import TimedRotatingFileHandler

# Set logging config
# Set logfile name
# logging.basicConfig(format='%(asctime)s — %(name)s — %(levelname)s — %(message)s')
FORMATTER = logging.Formatter("%(asctime)s — %(name)s — %(levelname)s — %(message)s")

def get_console_handler():
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(FORMATTER)
    return console_handler

def get_file_handler(file_name):
    file_handler = TimedRotatingFileHandler(file_name, when='midnight')
    file_handler.setFormatter(FORMATTER)
    return file_handler

def get_logger(logger_name,log_level,log_to_console,log_file_name):
    logger = logging.getLogger(logger_name)
    # Logging levels : DEBUG,INFO,WARNING,ERROR,CRITICAL
    # Set log_level to logging.DEBUG
    # log to both console and file
    logger.setLevel(log_level)
    if log_to_console:
        logger.addHandler(get_console_handler())
    logger.addHandler(get_file_handler(log_file_name))
    # No need to propagate the error up to parent
    logger.propagate = False
    return logger
