"""Subprocess management service for Swift CLI execution"""

import asyncio
import shlex
from pathlib import Path
from typing import List, Optional, Tuple, Dict, Any

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class SubprocessResult:
    """Result of subprocess execution"""
    
    def __init__(self, returncode: int, stdout: str, stderr: str, command: List[str]):
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
        command: List[str],
        timeout: Optional[int] = None,
        cwd: Optional[Path] = None,
        env: Optional[Dict[str, str]] = None,
        retries: Optional[int] = None
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
            Exception: For other execution errors
        """
        if timeout is None:
            timeout = self.default_timeout
        if retries is None:
            retries = self.max_retries
        
        logger.info(
            "Executing command",
            extra={
                "command": " ".join(command),
                "timeout": timeout,
                "cwd": str(cwd) if cwd else None,
                "retries": retries
            }
        )
        
        last_exception = None
        
        for attempt in range(retries + 1):
            try:
                # Execute the command
                process = await asyncio.create_subprocess_exec(
                    *command,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    cwd=cwd,
                    env=env
                )
                
                # Wait for completion with timeout
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=timeout
                )
                
                # Decode output
                stdout_text = stdout.decode('utf-8') if stdout else ""
                stderr_text = stderr.decode('utf-8') if stderr else ""
                
                result = SubprocessResult(
                    returncode=process.returncode,
                    stdout=stdout_text,
                    stderr=stderr_text,
                    command=command
                )
                
                if result.success:
                    logger.info(
                        "Command executed successfully",
                        extra={
                            "command": " ".join(command),
                            "returncode": result.returncode,
                            "attempt": attempt + 1,
                            "stdout_length": len(result.stdout),
                            "stderr_length": len(result.stderr)
                        }
                    )
                else:
                    logger.warning(
                        "Command failed",
                        extra={
                            "command": " ".join(command),
                            "returncode": result.returncode,
                            "attempt": attempt + 1,
                            "stderr": result.stderr
                        }
                    )
                
                return result
                
            except asyncio.TimeoutError as e:
                last_exception = e
                logger.warning(
                    "Command timed out",
                    extra={
                        "command": " ".join(command),
                        "timeout": timeout,
                        "attempt": attempt + 1
                    }
                )
                
                # Kill the process if it's still running
                if 'process' in locals():
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
                            "max_retries": retries
                        }
                    )
                    await asyncio.sleep(1)  # Brief delay before retry
                    continue
                
            except Exception as e:
                last_exception = e
                logger.error(
                    "Command execution failed",
                    extra={
                        "command": " ".join(command),
                        "error": str(e),
                        "attempt": attempt + 1
                    }
                )
                
                if attempt < retries:
                    logger.info(
                        "Retrying command after error",
                        extra={
                            "command": " ".join(command),
                            "attempt": attempt + 1,
                            "max_retries": retries
                        }
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
                extra={
                    "swift_cli_path": self.swift_cli_path,
                    "error": str(e)
                }
            )
            raise
    
    async def convert_docc_to_markdown(
        self,
        input_path: Path,
        output_path: Path,
        workspace: Path,
        timeout: Optional[int] = None
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
        command = [
            self.swift_cli_path,
            str(input_path),
            str(output_path)
        ]
        
        logger.info(
            "Starting DocC to Markdown conversion",
            extra={
                "input_path": str(input_path),
                "output_path": str(output_path),
                "workspace": str(workspace),
                "command": " ".join(command)
            }
        )
        
        result = await self.execute_command(
            command=command,
            cwd=workspace,
            timeout=timeout
        )
        
        if result.success:
            logger.info(
                "DocC conversion completed successfully",
                extra={
                    "input_path": str(input_path),
                    "output_path": str(output_path),
                    "output_size": output_path.stat().st_size if output_path.exists() else 0
                }
            )
        else:
            logger.error(
                "DocC conversion failed",
                extra={
                    "input_path": str(input_path),
                    "output_path": str(output_path),
                    "returncode": result.returncode,
                    "stderr": result.stderr
                }
            )
        
        return result
    
    def validate_command_safety(self, command: List[str]) -> bool:
        """
        Validate that a command is safe to execute
        
        Args:
            command: Command to validate
            
        Returns:
            bool: True if command is safe
        """
        # Only allow specific commands for security
        allowed_commands = {
            self.swift_cli_path: ["--version", "--help"]
        }
        
        if not command:
            return False
        
        base_command = command[0]
        
        # Check if base command is allowed
        if base_command not in allowed_commands:
            logger.warning(
                "Command not allowed for security",
                extra={
                    "base_command": base_command,
                    "allowed_commands": list(allowed_commands.keys())
                }
            )
            return False
        
        # For Swift CLI, allow additional arguments for conversion
        if base_command == self.swift_cli_path:
            # Allow: docc2context input.zip output.md
            if len(command) == 3 and not command[1].startswith('-'):
                return True
            # Allow: docc2context --version or --help
            if len(command) == 2 and command[1] in allowed_commands[base_command]:
                return True
        
        return False


# Global subprocess manager instance
subprocess_manager = SubprocessManager()
