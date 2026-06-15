import logging
import logging.config
import json
import os
from typing import Any, Dict
from datetime import datetime


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        if hasattr(record, "user_id"):
            log_data["user_id"] = record.user_id

        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id

        if record.extra:
            log_data.update(record.extra)

        return json.dumps(log_data)


class CustomLogRecord(logging.LogRecord):
    """Custom LogRecord to support extra fields."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.extra = {}


logging.setLogRecordFactory(CustomLogRecord)


def setup_logging(level: str = "INFO") -> None:
    """Configure application logging."""

    log_level = getattr(logging, level.upper(), logging.INFO)

    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            },
            "json": {
                "()": JSONFormatter,
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": log_level,
                "formatter": "json",
                "stream": "ext://sys.stdout",
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": log_level,
                "formatter": "json",
                "filename": f"{log_dir}/app.log",
                "maxBytes": 10485760,
                "backupCount": 10,
            },
            "error_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": logging.ERROR,
                "formatter": "json",
                "filename": f"{log_dir}/error.log",
                "maxBytes": 10485760,
                "backupCount": 10,
            },
        },
        "loggers": {
            "": {
                "level": log_level,
                "handlers": ["console", "file", "error_file"],
            },
            "uvicorn": {
                "level": logging.INFO,
                "handlers": ["console", "file"],
            },
            "uvicorn.access": {
                "level": logging.INFO,
                "handlers": ["console", "file"],
                "propagate": False,
            },
            "sqlalchemy": {
                "level": logging.WARNING,
                "handlers": ["console", "file"],
            },
        },
    }

    logging.config.dictConfig(config)
    logger = logging.getLogger(__name__)
    logger.info(f"Logging initialized with level: {level}")
