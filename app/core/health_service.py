"""Health service for monitoring application health"""

import logging

logger = logging.getLogger(__name__)


class HealthService:
    """Monitors and reports application health status"""

    def check_health(self, force_failure: bool = False) -> dict:
        """
        Check the health of the application.

        Args:
            force_failure: If True, force a health check failure for testing.

        Returns:
            A dictionary containing the health status.

        Raises:
            RuntimeError: If the health check fails.
        """
        if force_failure:
            logger.error("Health check failed (forced)")
            raise RuntimeError("Health check failed")

        logger.info("Health check passed")
        return {"status": "healthy"}
