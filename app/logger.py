"""
Production-ready logging configuration
"""
import logging
import logging.config
import json
from pythonjsonlogger import jsonlogger
from app.config import settings
from datetime import datetime

# Ensure logs directory exists
import os
os.makedirs("logs", exist_ok=True)

LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Configure logging handlers
logging.config.dictConfig({
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": LOG_FORMAT,
            "datefmt": "%Y-%m-%d %H:%M:%S"
        },
        "json": {
            "class": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "format": LOG_FORMAT
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": settings.LOG_LEVEL,
            "formatter": "default",
            "stream": "ext://sys.stdout"
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "DEBUG",
            "formatter": "json",
            "filename": "logs/app.log",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
            "encoding": "utf-8"
        },
        "error_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "ERROR",
            "formatter": "json",
            "filename": "logs/error.log",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
            "encoding": "utf-8"
        }
    },
    "loggers": {
        "": {
            "level": settings.LOG_LEVEL,
            "handlers": ["console", "file", "error_file"]
        },
        "app": {
            "level": settings.LOG_LEVEL,
            "handlers": ["console", "file", "error_file"],
            "propagate": False
        },
        "uvicorn.access": {
            "level": "INFO",
            "handlers": ["file"],
            "propagate": False
        }
    }
})

def get_logger(name: str) -> logging.Logger:
    """Get a logger instance"""
    return logging.getLogger(name)
