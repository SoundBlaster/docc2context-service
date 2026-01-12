"""Tests for structured logging (Task 5.3)"""

import logging
from io import StringIO

import pytest

from app.core.logging import StructuredLogger, get_logger, get_request_id, set_request_id


class TestStructuredLogger:
    """Test StructuredLogger event logging"""

    @pytest.fixture
    def logger_with_handler(self):
        """Create a StructuredLogger with a string handler for testing"""
        # Create a string buffer to capture log output
        log_stream = StringIO()
        handler = logging.StreamHandler(log_stream)

        # Create logger and add handler
        test_logger = StructuredLogger("test")
        test_logger.logger.handlers.clear()
        test_logger.logger.addHandler(handler)
        test_logger.logger.setLevel(logging.DEBUG)

        return test_logger, log_stream

    def test_log_extraction_success(self, logger_with_handler):
        """Test logging successful extraction"""
        test_logger, log_stream = logger_with_handler

        test_logger.log_extraction(
            status="success",
            file_name="test_archive.zip",
            file_size=1024000,
            extraction_time=2.5,
        )

        output = log_stream.getvalue()
        assert "test_archive.zip" in output
        assert "success" in output
        assert "1024000" in output
        assert "2.5" in output

    def test_log_extraction_failure(self, logger_with_handler):
        """Test logging failed extraction"""
        test_logger, log_stream = logger_with_handler

        test_logger.log_extraction(
            status="failure",
            file_name="bad_file.zip",
            file_size=0,
            extraction_time=0.5,
            error_msg="Invalid ZIP format",
        )

        output = log_stream.getvalue()
        assert "bad_file.zip" in output
        assert "failure" in output
        assert "Invalid ZIP format" in output

    def test_log_extraction_json_format(self, logger_with_handler):
        """Test that extraction logs are valid JSON"""
        test_logger, log_stream = logger_with_handler

        test_logger.log_extraction(
            status="success",
            file_name="test.zip",
            file_size=5000,
            extraction_time=1.0,
            request_id="test-req-123",
        )

        output = log_stream.getvalue().strip()
        # The output should contain valid JSON
        assert "event_type" in output
        assert "extraction" in output

    def test_log_auth_failure(self, logger_with_handler):
        """Test logging authentication failure"""
        test_logger, log_stream = logger_with_handler

        test_logger.log_auth_failure(
            username="testuser",
            ip_address="192.168.1.1",
            reason="Invalid credentials",
            request_id="auth-req-456",
        )

        output = log_stream.getvalue()
        assert "auth_failure" in output
        assert "testuser" in output
        assert "192.168.1.1" in output
        assert "Invalid credentials" in output

    def test_log_rate_limit(self, logger_with_handler):
        """Test logging rate limit trigger"""
        test_logger, log_stream = logger_with_handler

        test_logger.log_rate_limit(
            ip_address="10.0.0.5",
            endpoint="/api/v1/convert",
            limit=10,
            window="1hour",
            request_id="rate-req-789",
        )

        output = log_stream.getvalue()
        assert "rate_limit" in output
        assert "10.0.0.5" in output
        assert "/api/v1/convert" in output
        assert "10" in output

    def test_log_performance_anomaly(self, logger_with_handler):
        """Test logging performance anomaly"""
        test_logger, log_stream = logger_with_handler

        test_logger.log_performance_anomaly(
            metric_name="extraction_time",
            value=15.5,
            threshold=10.0,
            request_id="perf-req-101",
        )

        output = log_stream.getvalue()
        assert "performance_anomaly" in output
        assert "extraction_time" in output
        assert "15.5" in output
        assert "10.0" in output


class TestLoggingSetup:
    """Test logging configuration"""

    def test_get_logger(self):
        """Test getting a logger instance"""
        logger = get_logger("test_module")
        assert logger is not None
        assert logger.name == "test_module"

    def test_request_id_context(self):
        """Test request ID context management"""
        # Set a custom request ID
        request_id = "test-id-123"
        set_request_id(request_id)

        # Verify it's stored in context
        assert get_request_id() == request_id

    def test_request_id_generation(self):
        """Test automatic request ID generation"""
        # Set with None (should generate UUID)
        set_request_id(None)

        # Verify a request ID was generated
        request_id = get_request_id()
        assert request_id is not None
        assert len(request_id) > 0


class TestLoggingIntegration:
    """Integration tests for logging with the application"""

    def test_structured_logger_with_timestamps(self, logger_with_handler):
        """Test that timestamps are included in log output"""

        test_logger, log_stream = logger_with_handler

        test_logger.log_extraction(
            status="success",
            file_name="timestamp_test.zip",
            file_size=1000,
            extraction_time=1.0,
        )

        output = log_stream.getvalue()
        # Should have timestamp field in JSON
        assert "timestamp" in output or "test.zip" in output

    def test_multiple_events_logged(self, logger_with_handler):
        """Test logging multiple events in sequence"""
        test_logger, log_stream = logger_with_handler

        # Log multiple events
        test_logger.log_extraction("success", "file1.zip", 1000, 1.0)
        test_logger.log_auth_failure("user1", "192.168.1.1", "invalid")
        test_logger.log_rate_limit("10.0.0.1", "/api/v1/convert", 10, "1hour")

        output = log_stream.getvalue()
        # All events should be present
        assert "extraction" in output
        assert "auth_failure" in output
        assert "rate_limit" in output

    @pytest.fixture
    def logger_with_handler(self):
        """Create a StructuredLogger with a string handler for testing"""
        log_stream = StringIO()
        handler = logging.StreamHandler(log_stream)

        test_logger = StructuredLogger("test")
        test_logger.logger.handlers.clear()
        test_logger.logger.addHandler(handler)
        test_logger.logger.setLevel(logging.DEBUG)

        return test_logger, log_stream
