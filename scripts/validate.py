#!/usr/bin/env python3
"""
DocC2Context Service - Project Validation Script

This script provides a comprehensive validation suite for the DocC2Context Service project.
It includes checks for:
+- Python environment and dependencies
+- FastAPI application structure
+- API endpoints
+- Static files
+- Configuration files
+- Docker setup
"""

import tempfile
import datetime

import os
import sys
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import importlib.util
import zipfile
import tempfile

class ProjectValidator:
    """Main validation class for the DocC2Context Service project."""

    def __init__(self, project_root: str = None, args=None):
        """Initialize the validator with the project root directory."""
        self.project_root = project_root or os.getcwd()
        self.verbose = False
        self.verbose_file = None
        self.args = args
        self.results = {
            'passed': 0,
            'failed': 0,
            'warnings': 0,
            'details': []
        }

    def set_verbose(self, verbose: bool = True, output_file: str = None):
        """Enable or disable verbose output."""
        self.verbose = verbose
        if verbose and output_file:
            self.verbose_file = open(output_file, 'w')
            self.verbose_file.write(f"DocC2Context Service Validation - {datetime.datetime.now()}\n")
            self.verbose_file.write("="*50 + "\n")

    def log(self, message: str, level: str = "info"):
        """Log a message with optional verbosity."""
        if not self.args.json:
            if level in ["error", "warning"]:
                print(f"[{level.upper()}] {message}")
            if self.verbose and level == "info":
                print(f"[{level.upper()}] {message}")
                if self.verbose_file:
                    self.verbose_file.write(f"[{level.upper()}] {message}\n")

    def add_result(self, check_name: str, passed: bool, details: str = "", level: str = "info"):
        """Add a validation result to the results dictionary."""
        result_type = "passed" if passed else "failed"
        if level == "warning":
            result_type = "warnings"

        self.results[result_type] += 1
        self.results['details'].append({
            'check': check_name,
            'passed': passed,
            'details': details,
            'level': level
        })

        status = "PASS" if passed else "FAIL"
        if level == "warning":
            status = "WARN"

        self.log(f"{status}: {check_name} - {details}", level)

    def validate_python_environment(self) -> bool:
        """Validate Python environment and dependencies."""
        self.log("Validating Python environment...")

        # Check Python version
        python_version = sys.version_info
        if python_version < (3, 10):
            self.add_result(
                "Python Version",
                False,
                f"Python {python_version.major}.{python_version.minor} is not supported. Requires Python 3.10+",
                "error"
            )
            return False
        self.add_result("Python Version", True, f"Python {python_version.major}.{python_version.minor}.{python_version.micro}")

        # Check required packages
        required_packages = ['fastapi', 'uvicorn', 'requests', 'pytest']
        for package in required_packages:
            try:
                spec = importlib.util.find_spec(package)
                if spec is None:
                    self.add_result(f"Package {package}", False, f"Package {package} not found", "error")
                else:
                    self.add_result(f"Package {package}", True, f"Package {package} found")
            except ImportError:
                self.add_result(f"Package {package}", False, f"Package {package} not found", "error")

        return True

    def validate_project_structure(self) -> bool:
        """Validate project directory structure."""
        self.log("Validating project structure...")

        required_dirs = [
            'app',
            'app/api',
            'app/core',
            'app/services',
            'app/static',
            'app/static/css',
            'app/static/js',
            'DOCS',
            'scripts'
        ]

        required_files = [
            'app/main.py',
            'app/api/v1/endpoints.py',
            'app/core/config.py',
            'app/services/health_service.py',
            'app/static/index.html',
            'app/static/js/upload.js',
            'app/static/css/style.css',
            'requirements.txt',
            'Dockerfile',
            'docker-compose.yml',
            'README.md'
        ]

        structure_valid = True

        # Check directories
        for dir_path in required_dirs:
            full_path = os.path.join(self.project_root, dir_path)
            if os.path.isdir(full_path):
                self.add_result(f"Directory {dir_path}", True, f"Directory {dir_path} exists")
            else:
                self.add_result(f"Directory {dir_path}", False, f"Directory {dir_path} not found", "error")
                structure_valid = False

        # Check files
        for file_path in required_files:
            full_path = os.path.join(self.project_root, file_path)
            if os.path.isfile(full_path):
                self.add_result(f"File {file_path}", True, f"File {file_path} exists")
            else:
                self.add_result(f"File {file_path}", False, f"File {file_path} not found", "error")
                structure_valid = False

        return structure_valid

    def validate_fastapi_app(self) -> bool:
        """Validate FastAPI application."""
        self.log("Validating FastAPI application...")

        try:
            # Import the FastAPI app
            sys.path.insert(0, self.project_root)

            # Suppress FastAPI logs if --json flag is used
            import logging
            if self.args.json:
                logging.disable(logging.CRITICAL)

            from app.main import app
            self.add_result("FastAPI App Import", True, "FastAPI app imported successfully")

            # Check if app is a FastAPI instance
            from fastapi import FastAPI
            if isinstance(app, FastAPI):
                self.add_result("FastAPI Instance", True, "App is a valid FastAPI instance")
            else:
                self.add_result("FastAPI Instance", False, "App is not a FastAPI instance", "error")
                return False

            return True

        except ImportError as e:
            self.add_result("FastAPI App Import", False, f"Failed to import FastAPI app: {str(e)}", "error")
            return False
        except Exception as e:
            self.add_result("FastAPI App Import", False, f"Unexpected error: {str(e)}", "error")
            return False
        finally:
            sys.path.remove(self.project_root)

    def validate_api_endpoints(self) -> bool:
        """Validate API endpoints using TestClient."""
        self.log("Validating API endpoints...")

        try:
            sys.path.insert(0, self.project_root)
            from fastapi.testclient import TestClient
            from app.main import app

            # Suppress FastAPI logs if --json flag is used
            import logging
            if self.args.json:
                logging.disable(logging.CRITICAL)

            client = TestClient(app)

            # Test health endpoint
            response = client.get('/api/v1/health')
            if response.status_code == 200:
                self.add_result("Health Endpoint", True, "Health endpoint returned 200")
            else:
                self.add_result("Health Endpoint", False, f"Health endpoint returned {response.status_code}", "error")

            # Test convert endpoint (should fail without file)
            response = client.post('/api/v1/convert')
            if response.status_code == 422:
                self.add_result("Convert Endpoint (No File)", True, "Convert endpoint correctly rejected request without file")
            else:
                self.add_result("Convert Endpoint (No File)", False, f"Convert endpoint returned unexpected status {response.status_code}", "warning")

            # Test static files
            static_files = ['/static/index.html', '/static/js/upload.js', '/static/css/style.css']
            for static_file in static_files:
                response = client.get(static_file)
                if response.status_code == 200:
                    self.add_result(f"Static File {static_file}", True, f"Static file {static_file} accessible")
                else:
                    self.add_result(f"Static File {static_file}", False, f"Static file {static_file} returned {response.status_code}", "error")

            return True

        except ImportError as e:
            self.add_result("API Endpoints", False, f"Failed to import required modules: {str(e)}", "error")
            return False
        except Exception as e:
            self.add_result("API Endpoints", False, f"Unexpected error testing endpoints: {str(e)}", "error")
            return False
        finally:
            sys.path.remove(self.project_root)

    def validate_docker_setup(self) -> bool:
        """Validate Docker setup files."""
        self.log("Validating Docker setup...")

        docker_files = ['Dockerfile', 'docker-compose.yml', '.dockerignore']
        docker_valid = True

        for docker_file in docker_files:
            file_path = os.path.join(self.project_root, docker_file)
            if os.path.isfile(file_path):
                self.add_result(f"Docker File {docker_file}", True, f"Docker file {docker_file} exists")

                # Basic content validation
                with open(file_path, 'r') as f:
                    content = f.read()
                    if len(content) > 0:
                        self.add_result(f"Docker File {docker_file} Content", True, f"Docker file {docker_file} has content")
                    else:
                        self.add_result(f"Docker File {docker_file} Content", False, f"Docker file {docker_file} is empty", "warning")
            else:
                self.add_result(f"Docker File {docker_file}", False, f"Docker file {docker_file} not found", "error")
                docker_valid = False

        return docker_valid

    def validate_configuration(self) -> bool:
        """Validate configuration files."""
        self.log("Validating configuration files...")

        config_files = ['requirements.txt', 'README.md']
        config_valid = True

        for config_file in config_files:
            file_path = os.path.join(self.project_root, config_file)
            if os.path.isfile(file_path):
                self.add_result(f"Config File {config_file}", True, f"Config file {config_file} exists")

                # Check requirements.txt for basic packages
                if config_file == 'requirements.txt':
                    with open(file_path, 'r') as f:
                        content = f.read()
                        required_packages = ['fastapi', 'uvicorn', 'requests']
                        for package in required_packages:
                            if package in content:
                                self.add_result(f"Requirements {package}", True, f"Package {package} in requirements.txt")
                            else:
                                self.add_result(f"Requirements {package}", False, f"Package {package} not in requirements.txt", "warning")
            else:
                self.add_result(f"Config File {config_file}", False, f"Config file {config_file} not found", "error")
                config_valid = False

        return config_valid

    def validate_test_files(self) -> bool:
        """Validate test files if they exist."""
        self.log("Validating test files...")

        test_dir = os.path.join(self.project_root, 'tests')
        if os.path.isdir(test_dir):
            self.add_result("Test Directory", True, "Test directory exists")

            # Look for test files
            test_files = []
            for root, dirs, files in os.walk(test_dir):
                for file in files:
                    if file.startswith('test_') and file.endswith('.py'):
                        test_files.append(os.path.join(root, file))

            if test_files:
                self.add_result("Test Files", True, f"Found {len(test_files)} test files")
                for test_file in test_files:
                    self.add_result(f"Test File {test_file}", True, f"Test file {test_file} exists")
            else:
                self.add_result("Test Files", False, "No test files found", "warning")
        else:
            self.add_result("Test Directory", False, "Test directory not found", "warning")

        return True

    def run_all_validations(self) -> Dict:
        """Run all validation checks and return results."""
        self.log("Starting project validation...", "info")

        # Run all validation methods
        self.validate_python_environment()
        self.validate_project_structure()
        self.validate_fastapi_app()
        self.validate_api_endpoints()
        self.validate_docker_setup()
        self.validate_configuration()
        self.validate_test_files()

        # Calculate summary
        total_checks = self.results['passed'] + self.results['failed'] + self.results['warnings']
        pass_percentage = (self.results['passed'] / total_checks * 100) if total_checks > 0 else 0

        if self.verbose:
            self.log(f"\nValidation Summary:", "info")
            self.log(f"Total Checks: {total_checks}", "info")
            self.log(f"Passed: {self.results['passed']} ({pass_percentage:.1f}%)", "info")
            self.log(f"Failed: {self.results['failed']}", "info")
            self.log(f"Warnings: {self.results['warnings']}", "info")

        if self.results['failed'] > 0:
            self.log("Validation completed with errors!", "error")
        elif self.results['warnings'] > 0:
            self.log("Validation completed with warnings!", "warning")
        else:
            self.log("Validation completed successfully!", "info")

        return self.results

    def print_results(self, results: Optional[Dict] = None):
        """Print validation results in a readable format."""
        results_to_print = results or self.results

        if self.verbose and not self.args.json:
            print("\n" + "="*50)
            print("DOC2CONTEXT SERVICE VALIDATION RESULTS")
            print("="*50)

            for detail in results_to_print['details']:
                status = "✓ PASS" if detail['passed'] else "✗ FAIL"
                if detail['level'] == 'warning':
                    status = "! WARN"

                print(f"{status}: {detail['check']}")
                if detail['details']:
                    print(f"       {detail['details']}")

            print("\n" + "="*50)
            print(f"Summary: {results_to_print['passed']} passed, {results_to_print['failed']} failed, {results_to_print['warnings']} warnings")
            print("="*50)

def main():
    """Main entry point for the validation script."""
    import argparse

    parser = argparse.ArgumentParser(description="DocC2Context Service Project Validator")
    parser.add_argument('--verbose', '-v', action='store_true', help="Enable verbose output")
    parser.add_argument('--output-file', '-o', help="Output file for verbose logging")
    parser.add_argument('--project-root', '-p', default=os.getcwd(), help="Project root directory")
    parser.add_argument('--json', '-j', action='store_true', help="Output results as JSON")

    args = parser.parse_args()

    validator = ProjectValidator(args.project_root, args)
    validator.set_verbose(args.verbose, args.output_file)

    results = validator.run_all_validations()

    # Close the verbose file handle if it was opened
    if validator.verbose_file:
        validator.verbose_file.close()

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        validator.print_results(results)

    # Return appropriate exit code
    if results['failed'] > 0:
        sys.exit(1)
    elif results['warnings'] > 0:
        sys.exit(0)  # Warnings don't fail the validation
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()