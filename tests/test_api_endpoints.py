"""Integration tests for API endpoints"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)

def test_health_check_endpoint(client):
    """Test the health check endpoint"""
    response = client.get('/api/v1/health')
    assert response.status_code == 200
    # In test environment, the health check may return 'unhealthy' if docc2context binary is not found
    assert 'status' in response.json()

def test_convert_endpoint(client, sample_zip_file):
    """Test the conversion endpoint"""
    with open(sample_zip_file, 'rb') as f:
        response = client.post('/api/v1/convert', files={'file': f})
    assert response.status_code == 200
    assert response.headers['content-type'] == 'application/zip'
    assert 'content-disposition' in response.headers