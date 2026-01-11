#!/usr/bin/env python3
"""
Environment Validation Script
Validates environment configuration and checks system dependencies
"""

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# ANSI color codes
RED = "\033[0;31m"
GREEN = "\033[0;32m"
YELLOW = "\033[1;33m"
BLUE = "\033[0;34m"
NC = "\033[0m"  # No Color


class EnvironmentValidator:
    """Validates environment configuration and dependencies"""

    def __init__(self, env_name: Optional[str] = None, verbose: bool = False):
        self.env_name = env_name or os.getenv("ENVIRONMENT", "development")
        self.verbose = verbose
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.checks_passed = 0
        self.checks_failed = 0

    def log(self, message: str, level: str = "INFO"):
        """Log a message with color coding"""
        if level == "ERROR":
            print(f"{RED}✗ {message}{NC}")
            self.errors.append(message)
            self.checks_failed += 1
        elif level == "WARNING":
            print(f"{YELLOW}⚠ {message}{NC}")
            self.warnings.append(message)
        elif level == "SUCCESS":
            print(f"{GREEN}✓ {message}{NC}")
            self.checks_passed += 1
        else:
            if self.verbose:
                print(f"{BLUE}ℹ {message}{NC}")

    def check_env_var(
        self,
        var_name: str,
        required: bool = True,
        var_type: type = str,
        valid_values: Optional[List[Any]] = None,
        min_value: Optional[Any] = None,
        max_value: Optional[Any] = None,
    ) -> Tuple[bool, Optional[Any]]:
        """Check if an environment variable is set and valid"""
        value = os.getenv(var_name)

        if value is None:
            if required:
                self.log(f"Missing required environment variable: {var_name}", "ERROR")
                return False, None
            else:
                self.log(f"Optional environment variable not set: {var_name}", "INFO")
                return True, None

        # Type conversion and validation
        try:
            if var_type == int:
                typed_value = int(value)
            elif var_type == float:
                typed_value = float(value)
            elif var_type == bool:
                typed_value = value.lower() in ("true", "1", "yes")
            elif var_type == list:
                typed_value = [x.strip() for x in value.split(",")]
            else:
                typed_value = value

            # Validate against allowed values
            if valid_values and typed_value not in valid_values:
                self.log(
                    f"{var_name}={value} is invalid. Valid values: {valid_values}",
                    "ERROR",
                )
                return False, None

            # Validate ranges for numeric types
            if var_type in (int, float):
                if min_value is not None and typed_value < min_value:
                    self.log(
                        f"{var_name}={value} is below minimum ({min_value})", "ERROR"
                    )
                    return False, None
                if max_value is not None and typed_value > max_value:
                    self.log(
                        f"{var_name}={value} exceeds maximum ({max_value})", "ERROR"
                    )
                    return False, None

            self.log(f"{var_name}={value} (valid)", "SUCCESS")
            return True, typed_value

        except (ValueError, TypeError) as e:
            self.log(f"{var_name}={value} has invalid type ({var_type.__name__})", "ERROR")
            return False, None

    def check_required_env_vars(self) -> bool:
        """Check all required environment variables"""
        print(f"\n{BLUE}=== Checking Environment Variables ==={NC}\n")

        # API Configuration
        self.check_env_var("API_HOST", required=False, var_type=str)
        self.check_env_var("API_PORT", required=False, var_type=int, min_value=1, max_value=65535)

        # File Upload Configuration
        self.check_env_var(
            "MAX_UPLOAD_SIZE_MB", required=False, var_type=int, min_value=1, max_value=1000
        )
        self.check_env_var(
            "MAX_DECOMPRESSED_SIZE_MB", required=False, var_type=int, min_value=1, max_value=5000
        )

        # Workspace Configuration
        workspace_path = self.check_env_var("WORKSPACE_BASE_PATH", required=False, var_type=str)
        if workspace_path[1] and not Path(workspace_path[1]).exists():
            self.log(f"WORKSPACE_BASE_PATH={workspace_path[1]} does not exist", "WARNING")

        self.check_env_var("WORKSPACE_PREFIX", required=False, var_type=str)

        # Subprocess Configuration
        self.check_env_var("SWIFT_CLI_PATH", required=False, var_type=str)
        self.check_env_var(
            "SUBPROCESS_TIMEOUT", required=False, var_type=int, min_value=10, max_value=600
        )
        self.check_env_var(
            "MAX_SUBPROCESS_RETRIES", required=False, var_type=int, min_value=0, max_value=10
        )

        # Logging
        self.check_env_var(
            "LOG_LEVEL",
            required=False,
            var_type=str,
            valid_values=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        )

        # CORS
        self.check_env_var("CORS_ORIGINS", required=False, var_type=str)

        # Security Configuration
        self.check_env_var(
            "ENVIRONMENT",
            required=False,
            var_type=str,
            valid_values=["development", "staging", "production"],
        )
        self.check_env_var("ALLOWED_HOSTS", required=False, var_type=str)
        self.check_env_var("RATE_LIMIT", required=False, var_type=int, min_value=1, max_value=10000)

        return self.checks_failed == 0

    def check_environment_specific_rules(self) -> bool:
        """Check environment-specific security and configuration rules"""
        print(f"\n{BLUE}=== Checking Environment-Specific Rules ({self.env_name}) ==={NC}\n")

        if self.env_name == "production":
            # Production security checks
            debug = os.getenv("DEBUG", "false").lower()
            if debug in ("true", "1", "yes"):
                self.log("DEBUG=true in production environment (security risk!)", "ERROR")

            cors_origins = os.getenv("CORS_ORIGINS", "*")
            if cors_origins == "*":
                self.log("CORS_ORIGINS=* in production (security risk!)", "ERROR")

            allowed_hosts = os.getenv("ALLOWED_HOSTS", "*")
            if allowed_hosts == "*":
                self.log("ALLOWED_HOSTS=* in production (security risk!)", "ERROR")

            log_level = os.getenv("LOG_LEVEL", "INFO")
            if log_level == "DEBUG":
                self.log("LOG_LEVEL=DEBUG in production (performance impact!)", "WARNING")

            self.log("Production security checks completed", "INFO")

        elif self.env_name == "staging":
            # Staging-specific checks
            self.log("Staging environment checks completed", "INFO")

        elif self.env_name == "development":
            # Development-specific checks
            self.log("Development environment checks completed", "INFO")

        return self.checks_failed == 0

    def check_docker(self) -> bool:
        """Check if Docker daemon is running"""
        print(f"\n{BLUE}=== Checking Docker ==={NC}\n")

        if not shutil.which("docker"):
            self.log("Docker not found in PATH", "WARNING")
            return True  # Not a hard requirement

        try:
            result = subprocess.run(
                ["docker", "info"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                self.log("Docker daemon is running", "SUCCESS")
                return True
            else:
                self.log("Docker daemon is not running", "WARNING")
                return True  # Not a hard requirement
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            self.log(f"Docker check failed: {e}", "WARNING")
            return True  # Not a hard requirement

    def check_disk_space(self, min_free_gb: int = 5) -> bool:
        """Check available disk space"""
        print(f"\n{BLUE}=== Checking Disk Space ==={NC}\n")

        try:
            import shutil

            workspace_path = os.getenv("WORKSPACE_BASE_PATH", "/tmp")
            stat = shutil.disk_usage(workspace_path)
            free_gb = stat.free / (1024**3)

            if free_gb < min_free_gb:
                self.log(
                    f"Low disk space on {workspace_path}: {free_gb:.2f}GB free (minimum: {min_free_gb}GB)",
                    "ERROR",
                )
                return False
            else:
                self.log(
                    f"Sufficient disk space on {workspace_path}: {free_gb:.2f}GB free",
                    "SUCCESS",
                )
                return True
        except Exception as e:
            self.log(f"Disk space check failed: {e}", "WARNING")
            return True  # Not a hard requirement

    def check_swift_cli(self) -> bool:
        """Check if Swift CLI is accessible"""
        print(f"\n{BLUE}=== Checking Swift CLI ==={NC}\n")

        swift_cli_path = os.getenv("SWIFT_CLI_PATH", "docc2context")

        # Check if in PATH
        cli_path = shutil.which(swift_cli_path)
        if not cli_path:
            self.log(f"Swift CLI '{swift_cli_path}' not found in PATH", "ERROR")
            self.log(f"Hint: Install docc2context or set SWIFT_CLI_PATH", "INFO")
            return False

        # Check if executable
        if not os.access(cli_path, os.X_OK):
            self.log(f"Swift CLI '{cli_path}' is not executable", "ERROR")
            return False

        self.log(f"Swift CLI found: {cli_path}", "SUCCESS")

        # Try to get version
        try:
            result = subprocess.run(
                [swift_cli_path, "--help"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                self.log("Swift CLI is executable and responding", "SUCCESS")
                return True
            else:
                self.log("Swift CLI failed to execute", "ERROR")
                return False
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            self.log(f"Swift CLI execution failed: {e}", "ERROR")
            return False

    def print_summary(self):
        """Print validation summary"""
        print(f"\n{BLUE}{'=' * 50}{NC}")
        print(f"{BLUE}ENVIRONMENT VALIDATION SUMMARY{NC}")
        print(f"{BLUE}{'=' * 50}{NC}\n")

        print(f"Environment: {BLUE}{self.env_name}{NC}")
        print(f"Checks passed: {GREEN}{self.checks_passed}{NC}")
        print(f"Checks failed: {RED}{self.checks_failed}{NC}")
        print(f"Warnings: {YELLOW}{len(self.warnings)}{NC}")

        if self.checks_failed > 0:
            print(f"\n{RED}✗ Environment validation failed{NC}")
            print(f"\nErrors ({len(self.errors)}):")
            for error in self.errors:
                print(f"  - {error}")

            if self.warnings:
                print(f"\nWarnings ({len(self.warnings)}):")
                for warning in self.warnings:
                    print(f"  - {warning}")

            print(f"\n{YELLOW}Fix the errors above and run validation again.{NC}")
            return False
        else:
            print(f"\n{GREEN}✓ All environment checks passed!{NC}")
            if self.warnings:
                print(f"\nWarnings ({len(self.warnings)}):")
                for warning in self.warnings:
                    print(f"  - {warning}")
            return True


def main():
    parser = argparse.ArgumentParser(description="Validate environment configuration")
    parser.add_argument(
        "--env",
        choices=["development", "staging", "production"],
        help="Environment to validate (default: from ENVIRONMENT variable or 'development')",
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Verbose output"
    )
    parser.add_argument(
        "--health-check",
        action="store_true",
        help="Run health checks (Docker, disk space, Swift CLI)",
    )
    parser.add_argument(
        "--check",
        choices=["docker", "disk", "swift"],
        help="Run specific health check only",
    )

    args = parser.parse_args()

    # Create validator
    validator = EnvironmentValidator(env_name=args.env, verbose=args.verbose)

    print(f"\n{BLUE}{'=' * 50}{NC}")
    print(f"{BLUE}ENVIRONMENT VALIDATION{NC}")
    print(f"{BLUE}{'=' * 50}{NC}")

    # Run checks
    success = True

    if args.check:
        # Run specific check
        if args.check == "docker":
            success = validator.check_docker()
        elif args.check == "disk":
            success = validator.check_disk_space()
        elif args.check == "swift":
            success = validator.check_swift_cli()
    elif args.health_check:
        # Run all health checks
        success = validator.check_docker()
        success = validator.check_disk_space() and success
        success = validator.check_swift_cli() and success
    else:
        # Run full validation
        success = validator.check_required_env_vars()
        success = validator.check_environment_specific_rules() and success
        success = validator.check_docker() and success
        success = validator.check_disk_space() and success
        success = validator.check_swift_cli() and success

    # Print summary
    validator.print_summary()

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
