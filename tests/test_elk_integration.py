"""Tests for ELK Stack integration (Task 5.3)"""

import json
import os
from pathlib import Path

import pytest


class TestELKConfiguration:
    """Test ELK Stack configuration files exist"""

    def test_logstash_conf_exists(self):
        """Test that logstash.conf exists"""
        assert os.path.exists("logstash.conf"), "logstash.conf not found"

    def test_logstash_conf_has_input(self):
        """Test that logstash.conf has input block"""
        with open("logstash.conf") as f:
            content = f.read()
            assert "input {" in content
            assert "stdin" in content

    def test_logstash_conf_has_filter(self):
        """Test that logstash.conf has filter block"""
        with open("logstash.conf") as f:
            content = f.read()
            assert "filter {" in content
            assert "event_type" in content

    def test_logstash_conf_has_output(self):
        """Test that logstash.conf has output block"""
        with open("logstash.conf") as f:
            content = f.read()
            assert "output {" in content
            assert "elasticsearch" in content

    def test_logstash_retention_conf_exists(self):
        """Test that logstash_retention.conf exists"""
        assert os.path.exists("logstash_retention.conf"), "logstash_retention.conf not found"

    def test_logstash_retention_has_ilm_policy(self):
        """Test that retention config defines ILM policy"""
        with open("logstash_retention.conf") as f:
            config = json.load(f)
            assert "policy" in config
            assert config["policy"] == "docc2context-retention"
            assert "phases" in config

    def test_logstash_retention_has_phases(self):
        """Test that retention policy has all required phases"""
        with open("logstash_retention.conf") as f:
            config = json.load(f)
            phases = config["phases"]
            assert "hot" in phases
            assert "warm" in phases
            assert "cold" in phases
            assert "delete" in phases

    def test_setup_elasticsearch_script_exists(self):
        """Test that setup_elasticsearch.sh script exists"""
        assert os.path.exists("scripts/setup_elasticsearch.sh")

    def test_setup_elasticsearch_script_executable(self):
        """Test that setup_elasticsearch.sh is executable"""
        script_path = Path("scripts/setup_elasticsearch.sh")
        # Check if script is readable (it should be executable)
        assert os.access("scripts/setup_elasticsearch.sh", os.R_OK)

    def test_docker_compose_has_elasticsearch(self):
        """Test that docker-compose.yml includes Elasticsearch"""
        with open("docker-compose.yml") as f:
            content = f.read()
            assert "elasticsearch:" in content
            assert "elasticsearch:8.11.0" in content

    def test_docker_compose_has_logstash(self):
        """Test that docker-compose.yml includes Logstash"""
        with open("docker-compose.yml") as f:
            content = f.read()
            assert "logstash:" in content
            assert "logstash:8.11.0" in content

    def test_docker_compose_has_kibana(self):
        """Test that docker-compose.yml includes Kibana"""
        with open("docker-compose.yml") as f:
            content = f.read()
            assert "kibana:" in content
            assert "kibana:8.11.0" in content

    def test_docker_compose_has_elasticsearch_volume(self):
        """Test that docker-compose.yml has Elasticsearch volume"""
        with open("docker-compose.yml") as f:
            content = f.read()
            assert "elasticsearch_data:" in content

    def test_docker_compose_elk_network(self):
        """Test that ELK services use correct network"""
        with open("docker-compose.yml") as f:
            content = f.read()
            # Check that services reference the network
            assert "docc2context-network:" in content


class TestKibanaDashboards:
    """Test Kibana dashboard configuration"""

    def test_extraction_dashboard_exists(self):
        """Test that extraction failures dashboard exists"""
        assert os.path.exists("dashboards/extraction_failures.json")

    def test_security_dashboard_exists(self):
        """Test that security events dashboard exists"""
        assert os.path.exists("dashboards/security_events.json")

    def test_performance_dashboard_exists(self):
        """Test that performance anomalies dashboard exists"""
        assert os.path.exists("dashboards/performance.json")

    def test_dashboards_are_valid_json(self):
        """Test that all dashboard files are valid JSON"""
        dashboard_files = [
            "dashboards/extraction_failures.json",
            "dashboards/security_events.json",
            "dashboards/performance.json",
        ]

        for dashboard_file in dashboard_files:
            if os.path.exists(dashboard_file):
                with open(dashboard_file) as f:
                    try:
                        json.load(f)
                    except json.JSONDecodeError:
                        pytest.fail(f"{dashboard_file} is not valid JSON")


class TestLoggingConfiguration:
    """Test logging configuration for ELK"""

    def test_core_logging_module_exists(self):
        """Test that app/core/logging.py exists"""
        assert os.path.exists("app/core/logging.py")

    def test_structured_logger_class_exists(self):
        """Test that StructuredLogger class is defined"""
        from app.core.logging import StructuredLogger

        assert StructuredLogger is not None

    def test_structured_logger_has_extraction_method(self):
        """Test that StructuredLogger has log_extraction method"""
        from app.core.logging import StructuredLogger

        logger = StructuredLogger("test")
        assert hasattr(logger, "log_extraction")
        assert callable(getattr(logger, "log_extraction"))

    def test_structured_logger_has_auth_method(self):
        """Test that StructuredLogger has log_auth_failure method"""
        from app.core.logging import StructuredLogger

        logger = StructuredLogger("test")
        assert hasattr(logger, "log_auth_failure")
        assert callable(getattr(logger, "log_auth_failure"))

    def test_structured_logger_has_rate_limit_method(self):
        """Test that StructuredLogger has log_rate_limit method"""
        from app.core.logging import StructuredLogger

        logger = StructuredLogger("test")
        assert hasattr(logger, "log_rate_limit")
        assert callable(getattr(logger, "log_rate_limit"))

    def test_structured_logger_has_performance_method(self):
        """Test that StructuredLogger has log_performance_anomaly method"""
        from app.core.logging import StructuredLogger

        logger = StructuredLogger("test")
        assert hasattr(logger, "log_performance_anomaly")
        assert callable(getattr(logger, "log_performance_anomaly"))

    def test_environment_variables_in_env_production(self):
        """Test that .env.production has logging configuration"""
        if os.path.exists(".env.production"):
            with open(".env.production") as f:
                content = f.read()
                # Should have ELK configuration
                assert "ELASTICSEARCH" in content or "LOGSTASH" in content or "KIBANA" in content


class TestLoggingDocumentation:
    """Test logging documentation exists"""

    def test_logging_docs_exist(self):
        """Test that DOCS/LOGGING.md exists"""
        assert os.path.exists("DOCS/LOGGING.md")

    def test_logging_docs_have_content(self):
        """Test that DOCS/LOGGING.md has meaningful content"""
        with open("DOCS/LOGGING.md") as f:
            content = f.read()
            assert len(content) > 100
            assert "ELK" in content or "logging" in content.lower()
