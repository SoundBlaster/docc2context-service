"""Structured JSON logging with request ID support"""

import logging
import sys
import uuid
from contextvars import ContextVar
from typing import Any, Dict

from pythonjsonlogger import jsonlogger

# Context variable to store request ID
request_id_var: ContextVar[str] = ContextVar("request_id", default="")


def get_request_id() -> str:
    """Get the current request ID from context"""
    return request_id_var.get("")


def set_request_id(request_id: str | None = None) -> str:
    """Set a request ID in context. If None, generates a new UUID."""
    if request_id is None:
        request_id = str(uuid.uuid4())
    request_id_var.set(request_id)
    return request_id


class RequestIDFilter(logging.Filter):
    """Logging filter to add request ID to log records"""

    def filter(self, record: logging.LogRecord) -> bool:
        # Only add request_id if it doesn't already exist
        if not hasattr(record, 'request_id'):
            record.request_id = get_request_id()
        return True


def setup_logging(log_level: str = "INFO") -> None:
    """Configure structured JSON logging"""
    
    # Create JSON formatter
    formatter = jsonlogger.JsonFormatter(
        "%(timestamp)s %(level)s %(name)s %(message)s %(request_id)s",
        timestamp=True
    )
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    
    # Remove existing handlers
    root_logger.handlers = []
    
    # Add console handler with JSON formatter
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    handler.addFilter(RequestIDFilter())
    root_logger.addHandler(handler)
    
    # Set levels for third-party loggers
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for a module"""
    return logging.getLogger(name)





