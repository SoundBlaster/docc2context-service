"""Health check service for system and binary status monitoring"""

import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.core.config import settings
from app.core.logging import get_logger
from app.services.subprocess_manager import subprocess_manager

logger = get_logger(__name__)


class HealthService:
    """Manages health checks for the application"""

    def __init__(self):
        self.workspace_path = Path(settings.workspace_base_path)

    async def check_swift_cli(self) -> dict[str, Any]:
        """
        Check Swift CLI binary availability

        Returns:
            Dict with check results
        """
        logger.info("Checking Swift CLI binary availability")

        try:
            result = await subprocess_manager.check_swift_binary()
            return {
                "status": "ok",
                "binary_detected": True,
                "binary_path": settings.swift_cli_path,
                "version": result.stdout.strip() if result.stdout else None,
                "error": None,
            }
        except Exception as e:
            logger.warning(
                "Swift CLI binary check failed",
                extra={"binary_path": settings.swift_cli_path, "error": str(e)},
            )
            return {
                "status": "error",
                "binary_detected": False,
                "binary_path": settings.swift_cli_path,
                "version": None,
                "error": str(e),
            }

    def check_disk_space(self) -> dict[str, Any]:
        """
        Check disk space availability (optional check)

        Returns:
            Dict with disk space information
        """
        logger.info("Checking disk space availability")

        try:
            stat = shutil.disk_usage(self.workspace_path)
            total_gb = stat.total / (1024**3)
            free_gb = stat.free / (1024**3)
            used_gb = stat.used / (1024**3)
            usage_percent = (used_gb / total_gb) * 100

            # Determine status based on available space
            if free_gb < 1.0:  # Less than 1GB free
                status = "error"
            elif free_gb < 5.0:  # Less than 5GB free
                status = "warning"
            else:
                status = "ok"

            return {
                "status": status,
                "total_gb": round(total_gb, 2),
                "free_gb": round(free_gb, 2),
                "used_gb": round(used_gb, 2),
                "usage_percent": round(usage_percent, 2),
                "workspace_path": str(self.workspace_path),
            }

        except Exception as e:
            logger.error(
                "Disk space check failed",
                extra={"workspace_path": str(self.workspace_path), "error": str(e)},
            )
            return {"status": "error", "error": str(e), "workspace_path": str(self.workspace_path)}

    def check_memory(self) -> dict[str, Any]:
        """
        Check memory availability (optional check)

        Returns:
            Dict with memory information
        """
        logger.info("Checking memory availability")

        try:
            # Try to get memory info (works on Unix-like systems)
            try:
                with open("/proc/meminfo") as f:
                    meminfo = f.read()

                total_kb = 0
                available_kb = 0

                for line in meminfo.split("\n"):
                    if line.startswith("MemTotal:"):
                        total_kb = int(line.split()[1])
                    elif line.startswith("MemAvailable:"):
                        available_kb = int(line.split()[1])

                total_gb = total_kb / (1024**2)
                available_gb = available_kb / (1024**2)
                used_gb = total_gb - available_gb
                usage_percent = (used_gb / total_gb) * 100

                # Determine status based on available memory
                if available_gb < 0.5:  # Less than 512MB available
                    status = "error"
                elif available_gb < 1.0:  # Less than 1GB available
                    status = "warning"
                else:
                    status = "ok"

                return {
                    "status": status,
                    "total_gb": round(total_gb, 2),
                    "available_gb": round(available_gb, 2),
                    "used_gb": round(used_gb, 2),
                    "usage_percent": round(usage_percent, 2),
                }

            except FileNotFoundError:
                # Fallback for systems without /proc/meminfo
                logger.warning("Memory info not available, skipping memory check")
                return {
                    "status": "skipped",
                    "error": "Memory information not available on this system",
                }

        except Exception as e:
            logger.error("Memory check failed", extra={"error": str(e)})
            return {"status": "error", "error": str(e)}

    def determine_overall_status(self, checks: dict[str, Any]) -> str:
        """
        Determine overall system status based on individual checks

        Args:
            checks: Dictionary of check results

        Returns:
            Overall status string
        """
        # Critical checks
        if checks.get("swift_cli", {}).get("status") == "error":
            return "unhealthy"

        # Count warnings and errors
        warnings = 0
        errors = 0

        for check_name, check_result in checks.items():
            if isinstance(check_result, dict):
                status = check_result.get("status")
                if status == "error":
                    errors += 1
                elif status == "warning":
                    warnings += 1

        # Determine overall status
        if errors > 0:
            return "unhealthy"
        elif warnings > 0:
            return "degraded"
        else:
            return "ready"

    async def get_health_status(self, include_system_checks: bool = False) -> dict[str, Any]:
        """
        Get comprehensive health status

        Args:
            include_system_checks: Whether to include optional system checks

        Returns:
            Complete health status dictionary
        """
        logger.info(
            "Generating health status", extra={"include_system_checks": include_system_checks}
        )

        # Core checks
        checks = {"swift_cli": await self.check_swift_cli()}

        # Optional system checks
        if include_system_checks:
            checks["disk_space"] = self.check_disk_space()
            checks["memory"] = self.check_memory()

        # Determine overall status
        overall_status = self.determine_overall_status(checks)

        # Build response
        response = {
            "status": overall_status,
            "binary_detected": checks["swift_cli"]["binary_detected"],
            "binary_path": checks["swift_cli"]["binary_path"],
            "checks": {"swift_cli": checks["swift_cli"]["status"]},
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        # Add optional checks if enabled
        if include_system_checks:
            response["checks"]["disk_space"] = checks.get("disk_space", {}).get("status", "skipped")
            response["checks"]["memory"] = checks.get("memory", {}).get("status", "skipped")

            # Add detailed system info
            if "disk_space" in checks:
                response["disk_space"] = {
                    "total_gb": checks["disk_space"]["total_gb"],
                    "free_gb": checks["disk_space"]["free_gb"],
                    "usage_percent": checks["disk_space"]["usage_percent"],
                }

            if "memory" in checks and checks["memory"]["status"] != "skipped":
                response["memory"] = {
                    "total_gb": checks["memory"]["total_gb"],
                    "available_gb": checks["memory"]["available_gb"],
                    "usage_percent": checks["memory"]["usage_percent"],
                }

        logger.info(
            "Health status generated",
            extra={
                "overall_status": overall_status,
                "binary_detected": response["binary_detected"],
                "checks_included": list(response["checks"].keys()),
            },
        )

        return response


# Global health service instance
health_service = HealthService()
