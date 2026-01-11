"""Workspace management service for secure file processing"""

import shutil
import uuid
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class WorkspaceManager:
    """Manages isolated workspaces for file processing"""

    def __init__(self):
        self.base_path = Path(settings.workspace_base_path)
        self.prefix = settings.workspace_prefix
        self.permissions = settings.workspace_permissions

    def _generate_workspace_name(self) -> str:
        """Generate a unique workspace name"""
        return f"{self.prefix}-{uuid.uuid4()}"

    def _create_workspace_directory(self, workspace_name: str) -> Path:
        """Create a workspace directory with secure permissions"""
        workspace_path = self.base_path / workspace_name

        try:
            # Create directory with secure permissions
            workspace_path.mkdir(mode=self.permissions, parents=True, exist_ok=False)

            logger.info(
                "Workspace directory created",
                extra={
                    "workspace_path": str(workspace_path),
                    "workspace_name": workspace_name,
                    "permissions": oct(self.permissions),
                },
            )

            return workspace_path

        except FileExistsError:
            logger.error(
                "Workspace directory already exists",
                extra={"workspace_path": str(workspace_path), "workspace_name": workspace_name},
            )
            raise
        except OSError as e:
            logger.error(
                "Failed to create workspace directory",
                extra={
                    "workspace_path": str(workspace_path),
                    "workspace_name": workspace_name,
                    "error": str(e),
                },
            )
            raise

    def _cleanup_workspace(self, workspace_path: Path) -> None:
        """Clean up a workspace directory"""
        try:
            if workspace_path.exists():
                shutil.rmtree(workspace_path)
                logger.info(
                    "Workspace directory cleaned up", extra={"workspace_path": str(workspace_path)}
                )
            else:
                logger.warning(
                    "Workspace directory does not exist for cleanup",
                    extra={"workspace_path": str(workspace_path)},
                )

        except OSError as e:
            logger.error(
                "Failed to cleanup workspace directory",
                extra={"workspace_path": str(workspace_path), "error": str(e)},
            )
            # Don't raise exception for cleanup failures to avoid masking original errors

    @asynccontextmanager
    async def create_workspace(self) -> AsyncGenerator[Path, None]:
        """
        Create an isolated workspace for file processing

        Yields:
            Path: The workspace directory path

        Example:
            async with workspace_manager.create_workspace() as workspace:
                # Use workspace for file operations
                file_path = workspace / "uploaded_file.zip"
                # ... process files ...
            # Workspace is automatically cleaned up
        """
        workspace_name = self._generate_workspace_name()
        workspace_path = None

        try:
            workspace_path = self._create_workspace_directory(workspace_name)
            yield workspace_path

        except Exception as e:
            logger.error(
                "Error in workspace context",
                extra={
                    "workspace_name": workspace_name,
                    "workspace_path": str(workspace_path) if workspace_path else None,
                    "error": str(e),
                },
            )
            raise

        finally:
            # Always cleanup, even if an error occurred
            if workspace_path:
                self._cleanup_workspace(workspace_path)

    def get_file_path(self, workspace: Path, filename: str) -> Path:
        """Get a safe file path within the workspace"""
        # Ensure the filename is safe and stays within workspace
        safe_filename = Path(filename).name  # Remove any path components
        return workspace / safe_filename

    def cleanup_orphaned_workspaces(self) -> int:
        """
        Clean up orphaned workspace directories

        Returns:
            int: Number of workspaces cleaned up
        """
        cleaned_count = 0

        try:
            if not self.base_path.exists():
                logger.info(
                    "Base path does not exist, no cleanup needed",
                    extra={"base_path": str(self.base_path)},
                )
                return 0

            # Find all directories matching our prefix
            for item in self.base_path.iterdir():
                if item.is_dir() and item.name.startswith(self.prefix):
                    try:
                        # Check if directory is empty or old (simple heuristic)
                        # For now, we'll clean all directories with our prefix
                        # In production, you might want age-based cleanup
                        shutil.rmtree(item)
                        cleaned_count += 1

                        logger.info(
                            "Cleaned up orphaned workspace",
                            extra={"workspace_path": str(item), "workspace_name": item.name},
                        )

                    except OSError as e:
                        logger.error(
                            "Failed to cleanup orphaned workspace",
                            extra={
                                "workspace_path": str(item),
                                "workspace_name": item.name,
                                "error": str(e),
                            },
                        )

            logger.info(
                "Orphaned workspace cleanup completed",
                extra={
                    "cleaned_count": cleaned_count,
                    "base_path": str(self.base_path),
                    "prefix": self.prefix,
                },
            )

            return cleaned_count

        except Exception as e:
            logger.error(
                "Error during orphaned workspace cleanup",
                extra={"base_path": str(self.base_path), "prefix": self.prefix, "error": str(e)},
            )
            return 0


# Global workspace manager instance
workspace_manager = WorkspaceManager()
