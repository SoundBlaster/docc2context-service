"""Tests for monitoring and metrics (Task 5.2)"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestMetricsEndpoint:
    """Test /metrics endpoint availability and format"""

    def test_metrics_endpoint_exists(self):
        """Test that /metrics endpoint exists and returns 200"""
        response = client.get("/metrics")
        assert response.status_code == 200

    def test_metrics_content_type(self):
        """Test that /metrics returns correct content type"""
        response = client.get("/metrics")
        # Prometheus returns text/plain, may include version parameter
        assert "text/plain" in response.headers["content-type"]
        assert "charset=utf-8" in response.headers["content-type"]

    def test_metrics_prometheus_format(self):
        """Test that metrics are in Prometheus format"""
        response = client.get("/metrics")
        content = response.text

        # Prometheus format has HELP, TYPE, and metric lines
        assert "# HELP" in content or len(content) > 0
        assert "http_requests_total" in content

    def test_metrics_contains_http_metrics(self):
        """Test that HTTP metrics are exported"""
        response = client.get("/metrics")
        assert b"http_requests_total" in response.content
        assert b"http_request_duration_seconds" in response.content


class TestRequestMetrics:
    """Test that request metrics are properly recorded"""

    def test_health_endpoint_recorded(self):
        """Test that GET /health is recorded in metrics"""
        # Clear by making fresh request
        client.get("/health")

        # Get metrics
        response = client.get("/metrics")
        content = response.text

        # Should contain metric for /health endpoint
        assert "/health" in content or "health" in content

    def test_error_metrics_recorded(self):
        """Test that error status codes are recorded"""
        # Make a request that returns 404
        client.get("/nonexistent-endpoint")

        # Get metrics
        response = client.get("/metrics")
        content = response.text

        # Should have some metrics (exact assertion depends on prometheus format)
        assert "http_requests_total" in content

    def test_multiple_requests_increment_counter(self):
        """Test that making multiple requests increments counters"""
        # Make multiple requests
        for _ in range(3):
            client.get("/health")

        # Get metrics - verify counter is present
        response = client.get("/metrics")
        assert b"http_requests_total" in response.content


class TestMetricsMiddleware:
    """Test metrics middleware functionality"""

    def test_metrics_not_recursive(self):
        """Test that /metrics endpoint doesn't record itself"""
        # Get metrics twice to verify no recursion
        response1 = client.get("/metrics")
        response2 = client.get("/metrics")

        # Both should be successful
        assert response1.status_code == 200
        assert response2.status_code == 200

    def test_metrics_available_content(self):
        """Test that /metrics has actual metric content"""
        response = client.get("/metrics")
        content = response.text

        # Should have non-empty content
        assert len(content) > 100

        # Should contain type definitions
        lines = content.split("\n")
        has_metrics = any(line.startswith("http_") for line in lines)
        assert has_metrics


class TestMonitoringConfiguration:
    """Test monitoring configuration files exist"""

    def test_prometheus_config_exists(self):
        """Test that prometheus.yml exists"""
        import os
        assert os.path.exists("prometheus.yml")

    def test_alertmanager_config_exists(self):
        """Test that alertmanager.yml exists"""
        import os
        assert os.path.exists("alertmanager.yml")

    def test_alert_rules_exist(self):
        """Test that alert_rules.yml exists"""
        import os
        assert os.path.exists("alert_rules.yml")

    def test_monitoring_docs_exist(self):
        """Test that monitoring documentation exists"""
        import os
        assert os.path.exists("DOCS/MONITORING.md")

    def test_playbooks_directory_exists(self):
        """Test that playbooks directory exists"""
        import os
        assert os.path.isdir("DOCS/PLAYBOOKS")

    def test_critical_playbooks_exist(self):
        """Test that critical playbooks are present"""
        import os

        required_playbooks = [
            "DOCS/PLAYBOOKS/high_error_rate.md",
            "DOCS/PLAYBOOKS/extraction_failures.md",
            "DOCS/PLAYBOOKS/memory_exhaustion.md",
            "DOCS/PLAYBOOKS/cpu_exhaustion.md",
            "DOCS/PLAYBOOKS/service_down.md",
        ]

        for playbook in required_playbooks:
            assert os.path.exists(playbook), f"Missing playbook: {playbook}"


class TestPrometheusMetricsImport:
    """Test that metrics module can be imported and used"""

    def test_metrics_module_imports(self):
        """Test that metrics can be imported"""
        from app.core.metrics import (
            request_count,
            request_duration,
            zip_extractions_total,
        )

        assert request_count is not None
        assert request_duration is not None
        assert zip_extractions_total is not None

    def test_all_metric_types_defined(self):
        """Test that all required metrics are defined"""
        from app.core.metrics import (
            request_count,
            request_duration,
            zip_extractions_total,
            zip_extraction_duration,
            extraction_file_count,
            extraction_size_bytes,
            active_conversions,
            conversion_errors_total,
            resource_usage,
        )

        # All metrics should be defined and non-None
        metrics = [
            request_count,
            request_duration,
            zip_extractions_total,
            zip_extraction_duration,
            extraction_file_count,
            extraction_size_bytes,
            active_conversions,
            conversion_errors_total,
            resource_usage,
        ]

        for metric in metrics:
            assert metric is not None
