import os
import logging
from datetime import datetime


# =========================
# LOG DIRECTORY
# =========================
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
LOG_DIR = os.path.join(BASE_DIR, "logs")

os.makedirs(LOG_DIR, exist_ok=True)


# =========================
# LOG FILE PATHS
# =========================
ERROR_LOG = os.path.join(LOG_DIR, "errors.log")
INDEX_LOG = os.path.join(LOG_DIR, "indexing.log")
QUERY_LOG = os.path.join(LOG_DIR, "queries.log")
SYSTEM_LOG = os.path.join(LOG_DIR, "system.log")


# =========================
# LOGGER FACTORY
# =========================
def get_logger(name: str, log_file: str = SYSTEM_LOG):
    """
    Create a reusable logger instance.
    """

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Avoid duplicate handlers
    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # File Handler
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger


# =========================
# SPECIALIZED LOGGERS
# =========================
def get_error_logger():
    return get_logger("ERROR", ERROR_LOG)


def get_index_logger():
    return get_logger("INDEX", INDEX_LOG)


def get_query_logger():
    return get_logger("QUERY", QUERY_LOG)


def get_system_logger():
    return get_logger("SYSTEM", SYSTEM_LOG)