"""Unit tests for the subprocess manager"""

import pytest
from unittest.mock import patch, MagicMock
import subprocess
from app.core.subprocess_manager import SubprocessManager

@pytest.fixture
def subprocess_manager():
    """Create a SubprocessManager instance for testing"""
    return SubprocessManager()

def test_run_command_success(subprocess_manager):
    """Test successful command execution"""
    with patch('subprocess.run') as mock_run:
        mock_run.return_value = MagicMock(returncode=0, stdout='Success')
        result = subprocess_manager.run_command(['echo', 'test'])
        assert result == 'Success'

def test_run_command_failure(subprocess_manager):
    """Test failed command execution"""
    with patch('subprocess.run') as mock_run:
        mock_run.side_effect = subprocess.CalledProcessError(1, 'false', stderr='Error')
        with pytest.raises(RuntimeError) as excinfo:
            subprocess_manager.run_command(['false'])
        assert 'Error' in str(excinfo.value)

def test_run_command_timeout(subprocess_manager):
    """Test command execution timeout"""
    with patch('subprocess.run') as mock_run:
        mock_run.side_effect = subprocess.TimeoutExpired('sleep', 10)
        with pytest.raises(TimeoutError) as excinfo:
            subprocess_manager.run_command(['sleep', '10'], timeout=1)
        assert 'Command timed out' in str(excinfo.value)