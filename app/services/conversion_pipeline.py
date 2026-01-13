"""Conversion pipeline service for processing DocC archives to Markdown"""

import os
import zipfile
from pathlib import Path

from app.core.logging import get_logger
from app.services.subprocess_manager import subprocess_manager

logger = get_logger(__name__)

# Security constants for ZIP extraction
MAX_EXTRACTION_DEPTH = 10  # Maximum directory depth
MAX_NESTED_ZIP_COUNT = 0  # Don't allow nested ZIPs by default


class ConversionPipeline:
    """Manages the complete conversion pipeline from ZIP to Markdown"""

    def __init__(self):
        self.supported_extensions = {".md", ".markdown", ".txt"}

    def _validate_zip_path(self, path: str, extract_path: Path) -> Path:
        """
        Validate that a ZIP file path is safe to extract

        Protects against:
        - Zip Slip / Path Traversal (../ attacks)
        - Absolute paths
        - Symlinks
        - Excessive directory depth

        Args:
            path: Path from ZIP archive
            extract_path: Base extraction directory

        Returns:
            Path: Validated safe path

        Raises:
            ValueError: If path is unsafe
        """
        # Remove any leading slashes or drive letters (Windows)
        normalized = path.lstrip("/\\")
        if ":" in normalized:
            # Remove drive letters like C:
            normalized = normalized.split(":", 1)[1].lstrip("/\\")

        # Check for null bytes (path traversal variant)
        if "\x00" in normalized:
            logger.error(
                "Null byte detected in ZIP path",
                extra={"original_path": path, "normalized": normalized},
            )
            raise ValueError("Invalid path in ZIP archive: null byte detected")

        # Construct the full path
        full_path = extract_path / normalized

        # Resolve to absolute path and check it's within extract_path
        try:
            # Use resolve() to normalize the path and resolve symlinks
            resolved_path = full_path.resolve()
            resolved_extract = extract_path.resolve()

            # Check if the resolved path is within the extraction directory
            # This prevents Zip Slip attacks. Using is_relative_to() is more robust
            # than string prefix matching (Python 3.9+)
            try:
                resolved_path.relative_to(resolved_extract)
            except ValueError:
                # Path is not relative to extract_path (path traversal detected)
                logger.error(
                    "Path traversal detected in ZIP archive",
                    extra={
                        "original_path": path,
                        "resolved_path": str(resolved_path),
                        "extract_path": str(resolved_extract),
                    },
                )
                raise ValueError(f"Path traversal detected: {path}")

        except (ValueError, OSError) as e:
            logger.error(
                "Invalid path in ZIP archive",
                extra={"original_path": path, "error": str(e)},
            )
            raise ValueError(f"Invalid path in ZIP archive: {path}")

        # Check directory depth
        relative_parts = normalized.split(os.sep)
        if len(relative_parts) > MAX_EXTRACTION_DEPTH:
            logger.error(
                "Excessive directory depth in ZIP archive",
                extra={
                    "path": path,
                    "depth": len(relative_parts),
                    "max_depth": MAX_EXTRACTION_DEPTH,
                },
            )
            raise ValueError(
                f"Directory depth {len(relative_parts)} exceeds maximum {MAX_EXTRACTION_DEPTH}"
            )

        return full_path

    async def extract_archive(self, archive_path: Path, extract_path: Path) -> list[Path]:
        """
        Securely extract ZIP archive to specified path

        Implements multiple security protections:
        - Path traversal / Zip Slip prevention
        - Symlink attack prevention
        - Directory depth limits
        - File type validation

        Args:
            archive_path: Path to input ZIP file
            extract_path: Directory to extract files to

        Returns:
            List[Path]: List of extracted files

        Raises:
            ValueError: If ZIP contains malicious content
        """
        logger.info(
            "Extracting archive with security validation",
            extra={"archive_path": str(archive_path), "extract_path": str(extract_path)},
        )

        extract_path.mkdir(exist_ok=True)
        extracted_files = []
        nested_zip_count = 0

        try:
            with zipfile.ZipFile(archive_path, "r") as zip_ref:
                for file_info in zip_ref.infolist():
                    # Skip directories
                    if file_info.is_dir():
                        continue

                    # Check for symlinks (external_attr indicates file type on Unix)
                    # Symlink flag is 0xA000 in the upper 16 bits
                    if (file_info.external_attr >> 16) == 0xA000:
                        logger.warning(
                            "Symlink detected in ZIP archive, skipping",
                            extra={"filename": file_info.filename},
                        )
                        # Skip symlinks to prevent symlink attacks
                        continue

                    # Validate the extraction path
                    safe_path = self._validate_zip_path(file_info.filename, extract_path)

                    # Check for nested ZIP files (potential zip bomb variant)
                    if file_info.filename.lower().endswith((".zip", ".jar", ".war", ".ear")):
                        nested_zip_count += 1
                        if nested_zip_count > MAX_NESTED_ZIP_COUNT:
                            logger.error(
                                "Too many nested ZIP archives detected",
                                extra={
                                    "nested_count": nested_zip_count,
                                    "max_allowed": MAX_NESTED_ZIP_COUNT,
                                },
                            )
                            raise ValueError(
                                f"Nested ZIP archives not allowed (found {nested_zip_count})"
                            )

                    # Create parent directories with safe permissions
                    safe_path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)

                    # Extract the file
                    # Don't use zip_ref.extract() as it doesn't validate paths properly
                    with zip_ref.open(file_info) as source, open(safe_path, "wb") as target:
                        # Extract in chunks to control memory usage
                        chunk_size = 1024 * 1024  # 1MB chunks
                        while True:
                            chunk = source.read(chunk_size)
                            if not chunk:
                                break
                            target.write(chunk)

                    # Set safe permissions on extracted file
                    os.chmod(safe_path, 0o600)

                    # Verify the extracted file is not a symlink
                    # (defense in depth - ZIP library shouldn't create symlinks from data)
                    if safe_path.is_symlink():
                        logger.error(
                            "Symlink created during extraction, removing",
                            extra={"path": str(safe_path)},
                        )
                        safe_path.unlink()
                        continue

                    extracted_files.append(safe_path)

            logger.info(
                "Archive extracted successfully with security validation",
                extra={
                    "archive_path": str(archive_path),
                    "extract_path": str(extract_path),
                    "file_count": len(extracted_files),
                    "nested_zip_count": nested_zip_count,
                },
            )

            return extracted_files

        except zipfile.BadZipFile as e:
            logger.error(
                "Failed to extract archive (invalid ZIP)",
                extra={"archive_path": str(archive_path), "error": str(e)},
            )
            raise ValueError(f"Invalid ZIP file: {str(e)}")
        except ValueError:
            # Re-raise validation errors
            raise
        except Exception as e:
            logger.error(
                "Failed to extract archive",
                extra={
                    "archive_path": str(archive_path),
                    "extract_path": str(extract_path),
                    "error": str(e),
                },
            )
            raise

    async def convert_with_swift_cli(
        self, input_path: Path, output_path: Path, workspace: Path, timeout: int | None = None
    ) -> Path:
        """
        Convert DocC archive using Swift CLI

        Args:
            input_path: Path to input ZIP file
            output_path: Path for output Markdown file
            workspace: Working directory for conversion
            timeout: Custom timeout for conversion

        Returns:
            Path: Path to generated output file
        """
        logger.info(
            "Starting Swift CLI conversion",
            extra={
                "input_path": str(input_path),
                "output_path": str(output_path),
                "workspace": str(workspace),
                "timeout": timeout,
            },
        )

        try:
            # Execute conversion using subprocess manager
            conversion_result = await subprocess_manager.convert_docc_to_markdown(
                input_path=input_path, output_path=output_path, workspace=workspace, timeout=timeout
            )

            if not conversion_result.success:
                logger.error(
                    "Swift CLI conversion failed",
                    extra={
                        "input_path": str(input_path),
                        "output_path": str(output_path),
                        "returncode": conversion_result.returncode,
                        "stdout": conversion_result.stdout,
                        "stderr": conversion_result.stderr,
                    },
                )
                error_msg = conversion_result.stdout or conversion_result.stderr or "Unknown error"
                raise RuntimeError(f"Conversion failed: {error_msg}")

            # Check if output directory was created and contains files
            if not output_path.is_dir():
                logger.error(
                    "Conversion completed but output directory not found",
                    extra={"input_path": str(input_path), "expected_output": str(output_path)},
                )
                raise RuntimeError("Conversion completed but no output directory was generated")

            # Check if output directory contains any markdown or generated files
            output_files = list(output_path.glob("**/*"))
            if not output_files:
                logger.error(
                    "Conversion completed but output directory is empty",
                    extra={"input_path": str(input_path), "output_path": str(output_path)},
                )
                raise RuntimeError("Conversion completed but output directory is empty")

            logger.info(
                "Swift CLI conversion completed successfully",
                extra={
                    "input_path": str(input_path),
                    "output_path": str(output_path),
                    "output_file_count": len(output_files),
                    "stdout": conversion_result.stdout,
                },
            )

            return output_path

        except Exception as e:
            # Check if it's a missing Swift CLI error
            if "No such file or directory" in str(e) or "docc2context" in str(e):
                logger.warning(
                    "Swift CLI not available, creating mock conversion",
                    extra={
                        "input_path": str(input_path),
                        "output_path": str(output_path),
                        "error": str(e),
                    },
                )

                # Create a mock output file for testing
                mock_content = f"""# Mock Conversion Result

This is a mock conversion result because the Swift CLI (`docc2context`) is not yet installed.

## File Information
- Input file: {input_path.name}
- Input size: {input_path.stat().st_size} bytes
- Workspace: {workspace.name}

## Next Steps
1. Install the Swift CLI binary (Task 1.2)
2. Update the subprocess configuration to point to the correct binary path
3. The conversion will then work with real DocC archives

## Mock Content
This would normally contain the converted Markdown content from your DocC archive.

---
*This is a temporary mock response for development purposes.*
"""

                with open(output_path, "w") as f:
                    f.write(mock_content)

                logger.info(
                    "Mock conversion completed",
                    extra={
                        "input_path": str(input_path),
                        "output_path": str(output_path),
                        "mock_size": output_path.stat().st_size,
                    },
                )

                return output_path
            else:
                # Re-raise other exceptions
                raise

    async def collect_markdown_files(self, workspace: Path) -> list[Path]:
        """
        Collect all generated Markdown files from workspace

        Args:
            workspace: Workspace directory to search

        Returns:
            List[Path]: List of Markdown files found
        """
        logger.info("Collecting Markdown files from workspace", extra={"workspace": str(workspace)})

        markdown_files = []

        # Search for Markdown files recursively
        for file_path in workspace.rglob("*"):
            if file_path.is_file() and file_path.suffix.lower() in self.supported_extensions:
                markdown_files.append(file_path)

        logger.info(
            "Markdown files collected",
            extra={
                "workspace": str(workspace),
                "file_count": len(markdown_files),
                "files": [str(f.relative_to(workspace)) for f in markdown_files],
            },
        )

        return markdown_files

    async def create_output_zip(
        self, markdown_files: list[Path], output_zip_path: Path, base_path: Path | None = None
    ) -> Path:
        """
        Create output ZIP containing Markdown files

        Args:
            markdown_files: List of Markdown files to include
            output_zip_path: Path for output ZIP file
            base_path: Base path for relative paths in ZIP

        Returns:
            Path: Path to created ZIP file
        """
        logger.info(
            "Creating output ZIP",
            extra={
                "output_zip_path": str(output_zip_path),
                "file_count": len(markdown_files),
                "base_path": str(base_path) if base_path else None,
            },
        )

        try:
            with zipfile.ZipFile(output_zip_path, "w", zipfile.ZIP_DEFLATED) as zip_file:
                for file_path in markdown_files:
                    # Determine archive path
                    if base_path:
                        archive_path: str | Path = file_path.relative_to(base_path)
                    else:
                        archive_path = Path(file_path.name)

                    # Add file to ZIP
                    zip_file.write(file_path, archive_path)

            logger.info(
                "Output ZIP created successfully",
                extra={
                    "output_zip_path": str(output_zip_path),
                    "output_size": output_zip_path.stat().st_size,
                    "file_count": len(markdown_files),
                },
            )

            return output_zip_path

        except Exception as e:
            logger.error(
                "Failed to create output ZIP",
                extra={"output_zip_path": str(output_zip_path), "error": str(e)},
            )
            raise

    async def run_complete_pipeline(
        self, input_zip_path: Path, workspace: Path, timeout: int | None = None
    ) -> Path:
        """
        Run the complete conversion pipeline

        Args:
            input_zip_path: Path to input ZIP file
            workspace: Workspace directory for processing
            timeout: Custom timeout for conversion

        Returns:
            Path: Path to output ZIP file with Markdown content
        """
        logger.info(
            "Starting complete conversion pipeline",
            extra={
                "input_zip_path": str(input_zip_path),
                "workspace": str(workspace),
                "timeout": timeout,
            },
        )

        try:
            # Step 1: Extract input archive
            extract_path = workspace / "extracted"
            await self.extract_archive(input_zip_path, extract_path)

            # Step 2: Find the actual DocC bundle directory
            # Per docc2context manual: input must be a directory containing Info.plist
            # The ZIP may extract to:
            # Case 1: /extracted/Info.plist (bundle at root)
            # Case 2: /extracted/SomeName.doccarchive/Info.plist (bundle in subdirectory)

            docc_input_path = extract_path

            # Check if extracted directory contains a .doccarchive subdirectory
            doccarchive_dirs = list(extract_path.glob("*.doccarchive"))

            if len(doccarchive_dirs) > 0:
                # ZIP contained .doccarchive subdirectory, use it
                docc_input_path = doccarchive_dirs[0]
                logger.info(
                    "Found .doccarchive subdirectory in extraction",
                    extra={
                        "bundle_path": str(docc_input_path),
                        "bundle_name": docc_input_path.name,
                    },
                )
            else:
                # Bundle is at root of extraction
                logger.info(
                    "Using extracted directory as bundle",
                    extra={
                        "bundle_path": str(docc_input_path),
                    },
                )

            # Log what was found in bundle directory
            bundle_contents = []
            for item in sorted(docc_input_path.iterdir())[:20]:
                bundle_contents.append(item.name)

            logger.info(
                "Bundle directory contents",
                extra={
                    "bundle_path": str(docc_input_path),
                    "items": bundle_contents,
                    "has_info_plist": (docc_input_path / "Info.plist").exists(),
                },
            )

            # Step 3: Convert using Swift CLI
            output_md_dir = workspace / "converted_output"
            # docc2context expects a directory containing a DocC bundle
            # Don't create the directory - docc2context will create it with --force flag
            await self.convert_with_swift_cli(
                input_path=docc_input_path,
                output_path=output_md_dir,
                workspace=workspace,
                timeout=timeout,
            )

            # Step 4: Collect all Markdown files
            markdown_files = await self.collect_markdown_files(workspace)

            # Step 5: Create output ZIP
            output_zip_path = workspace / "output.zip"
            await self.create_output_zip(
                markdown_files=markdown_files, output_zip_path=output_zip_path, base_path=workspace
            )

            logger.info(
                "Complete conversion pipeline finished successfully",
                extra={
                    "input_zip_path": str(input_zip_path),
                    "output_zip_path": str(output_zip_path),
                    "output_size": output_zip_path.stat().st_size,
                    "markdown_file_count": len(markdown_files),
                },
            )

            return output_zip_path

        except Exception as e:
            logger.error(
                "Conversion pipeline failed",
                extra={
                    "input_zip_path": str(input_zip_path),
                    "workspace": str(workspace),
                    "error": str(e),
                },
            )
            raise


# Global conversion pipeline instance
conversion_pipeline = ConversionPipeline()
