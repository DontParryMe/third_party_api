import logging
import sys
from ..core.config import settings

LOG_FORMAT = "%(asctime)s | %(levelname)-8s | " "%(name)s:%(lineno)d | %(message)s"


def setup_logging() -> None:
    root_logger = logging.getLogger()
    root_logger.setLevel(settings.LOG_LEVEL)

    if root_logger.handlers:
        return

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(settings.LOG_LEVEL)
    handler.setFormatter(logging.Formatter(LOG_FORMAT))

    root_logger.addHandler(handler)

    logging.getLogger("httpx").propagate = False
    logging.getLogger("httpx").setLevel(logging.WARNING)


def get_logger(name: str = __name__) -> logging.Logger:
    return logging.getLogger(name)
