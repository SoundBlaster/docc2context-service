"""Subprocess management service for Swift CLI execution"""

import asyncio
from pathlib import Path

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class SubprocessResult:
    """Result of subprocess execution"""

    def __init__(self, returncode: int, stdout: str, stderr: str, command: list[str]):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr
        self.command = command
        self.success = returncode == 0

    def __str__(self) -> str:
        return f"SubprocessResult(returncode={self.returncode}, success={self.success})"


class SubprocessManager:
    """Manages subprocess execution with timeout and error handling"""

    def __init__(self):
        self.swift_cli_path = settings.swift_cli_path
        self.default_timeout = settings.subprocess_timeout
        self.max_retries = settings.max_subprocess_retries

    async def execute_command(
        self,
        command: list[str],
        timeout: int | None = None,
        cwd: Path | None = None,
        env: dict[str, str] | None = None,
        retries: int | None = None,
    ) -> SubprocessResult:
        """
        Execute a command with timeout and retry logic

        Args:
            command: Command to execute as list of strings
            timeout: Timeout in seconds (uses default if None)
            cwd: Working directory for command
            env: Environment variables for command
            retries: Number of retry attempts (uses default if None)

        Returns:
            SubprocessResult: Execution result

        Raises:
            asyncio.TimeoutError: If command times out
            ValueError: If command is unsafe
            Exception: For other execution errors
        """
        if timeout is None:
            timeout = self.default_timeout
        if retries is None:
            retries = self.max_retries

        # Validate command safety before execution
        if not self.validate_command_safety(command):
            logger.error(
                "Unsafe command blocked",
                extra={"command": " ".join(command)},
            )
            raise ValueError(f"Command not allowed for security reasons: {command[0]}")

        # Sanitize environment variables to prevent injection
        safe_env = None
        if env:
            safe_env = self._sanitize_environment(env)

        logger.info(
            "Executing command",
            extra={
                "command": " ".join(command),
                "timeout": timeout,
                "cwd": str(cwd) if cwd else None,
                "retries": retries,
            },
        )

        last_exception = None

        for attempt in range(retries + 1):
            try:
                # Execute the command with shell=False to prevent command injection
                process = await asyncio.create_subprocess_exec(
                    *command,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    cwd=cwd,
                    env=safe_env,
                )

                # Wait for completion with timeout
                stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=timeout)

                # Decode output
                stdout_text = stdout.decode("utf-8") if stdout else ""
                stderr_text = stderr.decode("utf-8") if stderr else ""

                result = SubprocessResult(
                    returncode=process.returncode,
                    stdout=stdout_text,
                    stderr=stderr_text,
                    command=command,
                )

                if result.success:
                    logger.info(
                        "Command executed successfully",
                        extra={
                            "command": " ".join(command),
                            "returncode": result.returncode,
                            "attempt": attempt + 1,
                            "stdout_length": len(result.stdout),
                            "stderr_length": len(result.stderr),
                        },
                    )
                else:
                    logger.warning(
                        "Command failed",
                        extra={
                            "command": " ".join(command),
                            "returncode": result.returncode,
                            "attempt": attempt + 1,
                            "stderr": result.stderr,
                        },
                    )

                return result

            except asyncio.TimeoutError as e:
                last_exception = e
                logger.warning(
                    "Command timed out",
                    extra={
                        "command": " ".join(command),
                        "timeout": timeout,
                        "attempt": attempt + 1,
                    },
                )

                # Kill the process if it's still running
                if "process" in locals():
                    try:
                        process.kill()
                        await process.wait()
                    except Exception:
                        pass

                if attempt < retries:
                    logger.info(
                        "Retrying command after timeout",
                        extra={
                            "command": " ".join(command),
                            "attempt": attempt + 1,
                            "max_retries": retries,
                        },
                    )
                    await asyncio.sleep(1)  # Brief delay before retry
                    continue

            except Exception as e:
                last_exception = e
                logger.error(
                    "Command execution failed",
                    extra={"command": " ".join(command), "error": str(e), "attempt": attempt + 1},
                )

                if attempt < retries:
                    logger.info(
                        "Retrying command after error",
                        extra={
                            "command": " ".join(command),
                            "attempt": attempt + 1,
                            "max_retries": retries,
                        },
                    )
                    await asyncio.sleep(1)  # Brief delay before retry
                    continue

        # All retries failed
        if isinstance(last_exception, asyncio.TimeoutError):
            raise asyncio.TimeoutError(
                f"Command '{' '.join(command)}' timed out after {timeout}s "
                f"after {retries + 1} attempts"
            )
        else:
            raise Exception(
                f"Command '{' '.join(command)}' failed after {retries + 1} attempts: "
                f"{str(last_exception)}"
            )

    async def check_swift_binary(self) -> SubprocessResult:
        """
        Check if Swift CLI binary is available and working

        Returns:
            SubprocessResult: Result of version check
        """
        try:
            return await self.execute_command([self.swift_cli_path, "--version"])
        except Exception as e:
            logger.error(
                "Swift CLI binary check failed",
                extra={"swift_cli_path": self.swift_cli_path, "error": str(e)},
            )
            raise

    async def convert_docc_to_markdown(
        self, input_path: Path, output_path: Path, workspace: Path, timeout: int | None = None
    ) -> SubprocessResult:
        """
        Convert DocC archive to Markdown using Swift CLI

        Args:
            input_path: Path to input ZIP file
            output_path: Path for output Markdown file
            workspace: Working directory for conversion
            timeout: Custom timeout for conversion

        Returns:
            SubprocessResult: Conversion result
        """
        command = [self.swift_cli_path, str(input_path), str(output_path)]

        logger.info(
            "Starting DocC to Markdown conversion",
            extra={
                "input_path": str(input_path),
                "output_path": str(output_path),
                "workspace": str(workspace),
                "command": " ".join(command),
            },
        )

        result = await self.execute_command(command=command, cwd=workspace, timeout=timeout)

        if result.success:
            logger.info(
                "DocC conversion completed successfully",
                extra={
                    "input_path": str(input_path),
                    "output_path": str(output_path),
                    "output_size": output_path.stat().st_size if output_path.exists() else 0,
                },
            )
        else:
            logger.error(
                "DocC conversion failed",
                extra={
                    "input_path": str(input_path),
                    "output_path": str(output_path),
                    "returncode": result.returncode,
                    "stderr": result.stderr,
                },
            )

        return result

    def _sanitize_environment(self, env: dict[str, str]) -> dict[str, str]:
        """
        Sanitize environment variables to prevent injection attacks

        Args:
            env: Environment variables to sanitize

        Returns:
            dict: Sanitized environment variables
        """
        safe_env = {}
        
        # Whitelist of safe environment variables
        safe_keys = {
            "PATH", "HOME", "USER", "LANG", "LC_ALL", "TZ",
            "TMPDIR", "TEMP", "TMP"
        }
        
        for key, value in env.items():
            # Only allow whitelisted keys
            if key not in safe_keys:
                logger.warning(
                    "Environment variable filtered",
                    extra={"key": key, "reason": "not in whitelist"},
                )
                continue
            
            # Check for null bytes
            if "\x00" in key or "\x00" in value:
                logger.warning(
                    "Environment variable contains null byte",
                    extra={"key": key},
                )
                continue
            
            # Limit value length to prevent memory exhaustion
            if len(value) > 4096:
                logger.warning(
                    "Environment variable value too long",
                    extra={"key": key, "length": len(value)},
                )
                continue
            
            safe_env[key] = value
        
        return safe_env

    def validate_command_safety(self, command: list[str]) -> bool:
        """
        Validate that a command is safe to execute

        Args:
            command: Command to validate

        Returns:
            bool: True if command is safe
        """
        if not command:
            return False

        # Validate each argument
        for arg in command:
            # Check for null bytes
            if "\x00" in arg:
                logger.warning(
                    "Null byte detected in command argument",
                    extra={"command": command, "arg": repr(arg)},
                )
                return False
            
            # Check argument length to prevent DoS
            if len(arg) > 4096:
                logger.warning(
                    "Command argument too long",
                    extra={"command": command, "arg_length": len(arg)},
                )
                return False

        base_command = command[0]

        # Only allow the Swift CLI binary
        if base_command != self.swift_cli_path:
            logger.warning(
                "Command not allowed for security",
                extra={
                    "base_command": base_command,
                    "allowed_command": self.swift_cli_path,
                },
            )
            return False

        # For Swift CLI, allow specific patterns
        # Pattern 1: docc2context input.zip output.md (conversion)
        if len(command) == 3:
            # Validate input and output paths don't contain dangerous characters
            input_path = command[1]
            output_path = command[2]
            
            # Check for command injection attempts
            dangerous_chars = [";", "&", "|", "`", "$", "(", ")", "<", ">", "\n", "\r"]
            for path in [input_path, output_path]:
                if any(char in path for char in dangerous_chars):
                    logger.warning(
                        "Dangerous characters detected in path",
                        extra={"path": path, "dangerous_chars": dangerous_chars},
                    )
                    return False
            
            return True
        
        # Pattern 2: docc2context --version or --help (info commands)
        if len(command) == 2 and command[1] in ["--version", "--help"]:
            return True

        logger.warning(
            "Command pattern not recognized",
            extra={"command": command},
        )
        return False


# Global subprocess manager instance
subprocess_manager = SubprocessManager()
