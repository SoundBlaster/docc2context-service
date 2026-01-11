"""Unit tests for the health service"""

import pytest
from app.core.health_service import HealthService

@pytest.fixture
def health_service():
    """Create a HealthService instance for testing"""
    return HealthService()

def test_check_health_success(health_service):
    """Test successful health check"""
    result = health_service.check_health()
    assert result == {'status': 'healthy'}

def test_check_health_failure(health_service):
    """Test failed health check"""
    with pytest.raises(RuntimeError) as excinfo:
        health_service.check_health(force_failure=True)
    assert 'Health check failed' in str(excinfo.value)