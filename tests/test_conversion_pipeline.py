"""Unit tests for the conversion pipeline"""

from unittest.mock import patch

import pytest

from app.core.conversion_pipeline import ConversionPipeline


@pytest.fixture
def conversion_pipeline():
    """Create a ConversionPipeline instance for testing"""
    return ConversionPipeline()


def test_convert_success(conversion_pipeline):
    """Test successful conversion"""
    with patch.object(conversion_pipeline.subprocess_manager, "run_command") as mock_run:
        mock_run.return_value = "Conversion successful"
        result = conversion_pipeline.convert("input.zip", "output.json")
        assert result == "output.json"


def test_convert_failure(conversion_pipeline):
    """Test failed conversion"""
    with patch.object(conversion_pipeline.subprocess_manager, "run_command") as mock_run:
        mock_run.side_effect = RuntimeError("Conversion failed")
        with pytest.raises(RuntimeError) as excinfo:
            conversion_pipeline.convert("input.zip", "output.json")
        assert "Conversion failed" in str(excinfo.value)


def test_convert_invalid_input(conversion_pipeline):
    """Test conversion with invalid input"""
    with pytest.raises(ValueError) as excinfo:
        conversion_pipeline.convert("", "output.json")
    assert "Invalid input file" in str(excinfo.value)
