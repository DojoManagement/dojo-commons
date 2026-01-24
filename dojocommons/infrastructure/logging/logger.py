import os
import sys

from loguru import logger

log_level = os.getenv("LOG_LEVEL", "INFO").upper()

logger.remove()

logger.add(sys.stdout, level=log_level, backtrace=True, diagnose=True)
