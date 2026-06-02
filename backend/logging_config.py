import logging
from logging.handlers import RotatingFileHandler

from .config import LOG_DIR


def setup_logger(name, filename):
    LOG_DIR.mkdir(exist_ok=True)
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.propagate = False
    if logger.handlers:
        return logger
    handler = RotatingFileHandler(LOG_DIR / filename, maxBytes=1_000_000, backupCount=5, encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    logger.addHandler(handler)
    return logger


RUNTIME_LOGGER = setup_logger("library.runtime", "runtime.log")
AUDIT_LOGGER = setup_logger("library.audit", "audit.log")
