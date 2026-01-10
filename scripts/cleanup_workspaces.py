#!/usr/bin/env python3
"""
Startup cleanup script for orphaned workspaces

This script can be run as:
1. A cron job for periodic cleanup
2. A container entrypoint script
3. Manually for maintenance

Usage:
    python scripts/cleanup_workspaces.py
"""

import sys
import os

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.services.workspace_manager import workspace_manager
from app.core.logging import setup_logging, get_logger

# Setup logging
setup_logging()
logger = get_logger(__name__)


def main():
    """Main cleanup function"""
    logger.info("Starting orphaned workspace cleanup")
    
    try:
        cleaned_count = workspace_manager.cleanup_orphaned_workspaces()
        
        if cleaned_count > 0:
            logger.info(
                f"Successfully cleaned up {cleaned_count} orphaned workspace(s)",
                extra={"cleaned_count": cleaned_count}
            )
        else:
            logger.info("No orphaned workspaces found")
            
        return 0
        
    except Exception as e:
        logger.error(
            "Workspace cleanup failed",
            extra={"error": str(e)}
        )
        return 1


if __name__ == "__main__":
    sys.exit(main())
