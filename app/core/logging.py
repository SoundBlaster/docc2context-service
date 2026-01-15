"""Structured JSON logging with request ID support"""

import logging
import sys
import uuid
from contextvars import ContextVar

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
        if not hasattr(record, "request_id"):
            record.request_id = get_request_id()
        return True


def setup_logging(log_level: str = "INFO") -> None:
    """Configure structured JSON logging"""

    # Create JSON formatter
    formatter = jsonlogger.JsonFormatter(
        "%(timestamp)s %(level)s %(name)s %(message)s %(request_id)s", timestamp=True
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


class StructuredLogger:
    """Wrapper for structured event logging with ELK-specific fields (Task 5.3)"""

    def __init__(self, name: str):
        self.logger = logging.getLogger(name)

    def log_extraction(
        self,
        status: str,
        file_name: str,
        file_size: int,
        extraction_time: float,
        error_msg: str | None = None,
        request_id: str | None = None,
    ):
        """Log extraction event for dashboard aggregation.

        Args:
            status: "success" or "failure"
            file_name: Name of the extracted file
            file_size: Size in bytes
            extraction_time: Extraction duration in seconds
            error_msg: Error message if status is failure
            request_id: Request ID for tracing
        """
        import json
        from datetime import datetime

        payload = {
            "event_type": "extraction",
            "status": status,
            "file_name": file_name,
            "file_size_bytes": file_size,
            "extraction_time_seconds": extraction_time,
            "timestamp": datetime.utcnow().isoformat(),
            "request_id": request_id or get_request_id(),
        }
        if error_msg:
            payload["error_message"] = error_msg

        level = logging.ERROR if status == "failure" else logging.INFO
        self.logger.log(level, json.dumps(payload))

    def log_auth_failure(
        self,
        username: str | None,
        ip_address: str,
        reason: str,
        request_id: str | None = None,
    ):
        """Log authentication failure for security dashboard.

        Args:
            username: Username attempted (or None for anonymous)
            ip_address: Client IP address
            reason: Reason for failure (invalid creds, blocked, etc.)
            request_id: Request ID for tracing
        """
        import json
        from datetime import datetime

        payload = {
            "event_type": "auth_failure",
            "username": username,
            "client_ip": ip_address,
            "reason": reason,
            "timestamp": datetime.utcnow().isoformat(),
            "request_id": request_id or get_request_id(),
        }
        self.logger.warning(json.dumps(payload))

    def log_rate_limit(
        self,
        ip_address: str,
        endpoint: str,
        limit: int,
        window: str,
        request_id: str | None = None,
    ):
        """Log rate limit trigger for security dashboard.

        Args:
            ip_address: Client IP that triggered limit
            endpoint: API endpoint being rate limited
            limit: Number of requests allowed
            window: Time window (e.g., "1hour", "1minute")
            request_id: Request ID for tracing
        """
        import json
        from datetime import datetime

        payload = {
            "event_type": "rate_limit",
            "client_ip": ip_address,
            "endpoint": endpoint,
            "limit": limit,
            "window": window,
            "timestamp": datetime.utcnow().isoformat(),
            "request_id": request_id or get_request_id(),
        }
        self.logger.warning(json.dumps(payload))

    def log_performance_anomaly(
        self,
        metric_name: str,
        value: float,
        threshold: float,
        request_id: str | None = None,
    ):
        """Log performance anomalies for monitoring dashboard.

        Args:
            metric_name: Name of the metric (e.g., "extraction_time", "memory_usage")
            value: Current metric value
            threshold: Threshold that was exceeded
            request_id: Request ID for tracing
        """
        import json
        from datetime import datetime

        payload = {
            "event_type": "performance_anomaly",
            "metric": metric_name,
            "value": value,
            "threshold": threshold,
            "timestamp": datetime.utcnow().isoformat(),
            "request_id": request_id or get_request_id(),
        }
        self.logger.warning(json.dumps(payload))
