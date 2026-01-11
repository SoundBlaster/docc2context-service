"""Unit tests for file validation service"""

import os
import tempfile
import zipfile

import pytest

from app.services.file_validation import (
    FileValidationError,
    sanitize_filename,
    validate_file_size,
    validate_zip_bomb_protection,
    validate_zip_magic_number,
)


@pytest.fixture
def valid_zip_file():
    """Create a valid ZIP file for testing"""
    with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as temp_file:
        with zipfile.ZipFile(temp_file, "w") as zipf:
            zipf.writestr("sample.txt", "This is a sample file.")
        yield temp_file.name
        os.unlink(temp_file.name)


@pytest.fixture
def invalid_file():
    """Create an invalid file for testing"""
    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as temp_file:
        temp_file.write(b"This is not a ZIP file.")
        yield temp_file.name
        os.unlink(temp_file.name)


def test_validate_file_size_valid():
    """Test validation of a valid file size"""
    validate_file_size(1024 * 1024)  # 1MB


def test_validate_file_size_invalid():
    """Test validation of an invalid file size"""
    with pytest.raises(FileValidationError):
        validate_file_size(100 * 1024 * 1024 + 1)  # 100MB + 1 byte


def test_validate_zip_magic_number_valid(valid_zip_file):
    """Test validation of a valid ZIP magic number"""
    with open(valid_zip_file, "rb") as f:
        content = f.read()
    validate_zip_magic_number(content)


def test_validate_zip_magic_number_invalid(invalid_file):
    """Test validation of an invalid ZIP magic number"""
    with open(invalid_file, "rb") as f:
        content = f.read()
    with pytest.raises(FileValidationError):
        validate_zip_magic_number(content)


def test_sanitize_filename_valid():
    """Test sanitization of a valid filename"""
    assert sanitize_filename("valid_file.zip") == "valid_file.zip"


def test_sanitize_filename_path_traversal():
    """Test sanitization of a filename with path traversal"""
    # The function should remove path components, not raise an exception
    assert sanitize_filename("../../../malicious.zip") == "malicious.zip"


def test_sanitize_filename_invalid_chars():
    """Test sanitization of a filename with invalid characters"""
    with pytest.raises(FileValidationError):
        sanitize_filename("invalid|chars.zip")


def test_validate_zip_bomb_protection_valid(valid_zip_file):
    """Test validation of a valid ZIP file for bomb protection"""
    with zipfile.ZipFile(valid_zip_file, "r") as zip_file:
        validate_zip_bomb_protection(zip_file, 1024)


def test_validate_zip_bomb_protection_invalid():
    """Test validation of an invalid ZIP file for bomb protection"""
    with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as temp_file:
        with zipfile.ZipFile(temp_file, "w") as zipf:
            # Create a large file to simulate a zip bomb
            zipf.writestr("large_file.txt", "0" * (100 * 1024 * 1024 + 1))  # 100MB + 1 byte
        with zipfile.ZipFile(temp_file.name, "r") as zip_file:
            with pytest.raises(FileValidationError):
                validate_zip_bomb_protection(zip_file, 1024)
        os.unlink(temp_file.name)
