"""Subprocess manager for running external commands"""

import subprocess
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class SubprocessManager:
    """Manages subprocess execution with error handling and logging"""

    def run_command(
        self,
        command: list[str],
        timeout: Optional[int] = None,
        capture_output: bool = True,
    ) -> str:
        """
        Run a command in a subprocess and return its output.

        Args:
            command: The command to run as a list of strings.
            timeout: Timeout in seconds for the command execution.
            capture_output: Whether to capture stdout and stderr.

        Returns:
            The stdout output of the command.

        Raises:
            RuntimeError: If the command fails.
            TimeoutError: If the command times out.
        """
        try:
            result = subprocess.run(
                command,
                timeout=timeout,
                capture_output=capture_output,
                text=True,
                check=True,
            )
            return result.stdout
        except subprocess.TimeoutExpired as e:
            logger.error(f"Command timed out: {' '.join(command)}")
            raise TimeoutError(f"Command timed out: {e}") from e
        except subprocess.CalledProcessError as e:
            logger.error(f"Command failed: {' '.join(command)}")
            logger.error(f"Error output: {e.stderr}")
            raise RuntimeError(f"Command failed: {e.stderr}") from e