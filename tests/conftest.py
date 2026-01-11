"""Test fixtures for DocC2Context Service"""

import os
import tempfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def temp_workspace():
    """Create a temporary workspace for testing"""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def sample_zip_file():
    """Create a sample ZIP file for testing"""
    import zipfile

    with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as temp_file:
        with zipfile.ZipFile(temp_file, "w") as zipf:
            zipf.writestr("sample.txt", "This is a sample file.")
        yield temp_file.name
        os.unlink(temp_file.name)


@pytest.fixture
def large_file():
    """Create a large file for testing file size limits"""
    with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as temp_file:
        # Create a file larger than the upload limit
        temp_file.write(b"0" * (100 * 1024 * 1024 + 1))  # 100MB + 1 byte
        yield temp_file.name
        os.unlink(temp_file.name)
