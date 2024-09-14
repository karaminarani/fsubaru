import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import logging.Logger


class PaddedLevelFormatter(logging.Formatter):
    def format(self, record) -> str:
        if record.levelname == "WARNING":
            record.levelname = "WARN".ljust(5)
        elif record.levelname == "INFO":
            record.levelname = record.levelname.ljust(5)

        # Clear exception info to avoid logging it twice
        record.exc_info = None

        return super().format(record)


class Logger:
    def __init__(self, log_name: str) -> None:
        self.log_name = log_name
        self.log_setup()

    def log_exception_handler(self, record) -> None:
        # Restart the application on certain errors
        exception_log = any(
            key in record.name for key in {"asyncio", "pymongo"}
        ) and record.levelname.strip() in {"WARN", "ERROR"}
        if exception_log:
            os.execvp(sys.executable, [sys.executable, *sys.argv])

    def log_setup(self) -> "logging.Logger":
        log_level = logging.INFO

        formatter = PaddedLevelFormatter(
            fmt="%(asctime)s [ %(levelname)s ] %(name)s -> %(message)s",
            datefmt="%Y-%m-%d | %X",
        )

        file_handler = RotatingFileHandler(
            "logs.txt", mode="a", maxBytes=4194304, backupCount=1, encoding="utf-8"
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(log_level)

        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        stream_handler.setLevel(log_level)

        exception_handler = logging.StreamHandler()
        exception_handler.setLevel(log_level)
        exception_handler.setFormatter(formatter)
        exception_handler.emit = self.log_exception_handler

        # Set up the basic configuration
        logging.basicConfig(
            level=log_level, handlers=[file_handler, stream_handler, exception_handler]
        )

        self.log = logging.getLogger(self.log_name)

        # Reduce logging level for noisy libraries
        logging.getLogger("apscheduler").setLevel(logging.WARNING)
        logging.getLogger("httpx").setLevel(logging.WARNING)
        logging.getLogger("hydrogram").setLevel(logging.WARNING)
        logging.getLogger("pymongo").setLevel(logging.WARNING)

        return self.log


logger: "Logger" = Logger(log_name="fsub.bot").log