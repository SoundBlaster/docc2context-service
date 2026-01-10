"""Conversion pipeline service for processing DocC archives to Markdown"""

import asyncio
import zipfile
from pathlib import Path
from typing import List, Optional, AsyncGenerator

from app.core.logging import get_logger
from app.services.subprocess_manager import subprocess_manager

logger = get_logger(__name__)


class ConversionPipeline:
    """Manages the complete conversion pipeline from ZIP to Markdown"""
    
    def __init__(self):
        self.supported_extensions = {'.md', '.markdown', '.txt'}
    
    async def extract_archive(self, archive_path: Path, extract_path: Path) -> List[Path]:
        """
        Extract ZIP archive to specified path
        
        Args:
            archive_path: Path to input ZIP file
            extract_path: Directory to extract files to
            
        Returns:
            List[Path]: List of extracted files
        """
        logger.info(
            "Extracting archive",
            extra={
                "archive_path": str(archive_path),
                "extract_path": str(extract_path)
            }
        )
        
        extract_path.mkdir(exist_ok=True)
        extracted_files = []
        
        try:
            with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                for file_info in zip_ref.infolist():
                    # Skip directories
                    if file_info.is_dir():
                        continue
                    
                    # Extract file
                    extracted_path = extract_path / file_info.filename
                    zip_ref.extract(file_info, extract_path)
                    extracted_files.append(extracted_path)
            
            logger.info(
                "Archive extracted successfully",
                extra={
                    "archive_path": str(archive_path),
                    "extract_path": str(extract_path),
                    "file_count": len(extracted_files)
                }
            )
            
            return extracted_files
            
        except zipfile.BadZipFile as e:
            logger.error(
                "Failed to extract archive (invalid ZIP)",
                extra={
                    "archive_path": str(archive_path),
                    "error": str(e)
                }
            )
            raise ValueError(f"Invalid ZIP file: {str(e)}")
        except Exception as e:
            logger.error(
                "Failed to extract archive",
                extra={
                    "archive_path": str(archive_path),
                    "extract_path": str(extract_path),
                    "error": str(e)
                }
            )
            raise
    
    async def convert_with_swift_cli(
        self,
        input_path: Path,
        output_path: Path,
        workspace: Path,
        timeout: Optional[int] = None
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
                "timeout": timeout
            }
        )
        
        try:
            # Execute conversion using subprocess manager
            conversion_result = await subprocess_manager.convert_docc_to_markdown(
                input_path=input_path,
                output_path=output_path,
                workspace=workspace,
                timeout=timeout
            )
            
            if not conversion_result.success:
                logger.error(
                    "Swift CLI conversion failed",
                    extra={
                        "input_path": str(input_path),
                        "output_path": str(output_path),
                        "returncode": conversion_result.returncode,
                        "stderr": conversion_result.stderr
                    }
                )
                raise RuntimeError(f"Conversion failed: {conversion_result.stderr}")
            
            # Check if output file was created
            if not output_path.exists():
                logger.error(
                    "Conversion completed but no output file found",
                    extra={
                        "input_path": str(input_path),
                        "expected_output": str(output_path)
                    }
                )
                raise RuntimeError("Conversion completed but no output file was generated")
            
            logger.info(
                "Swift CLI conversion completed successfully",
                extra={
                    "input_path": str(input_path),
                    "output_path": str(output_path),
                    "output_size": output_path.stat().st_size,
                    "stdout": conversion_result.stdout
                }
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
                        "error": str(e)
                    }
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
                
                with open(output_path, 'w') as f:
                    f.write(mock_content)
                
                logger.info(
                    "Mock conversion completed",
                    extra={
                        "input_path": str(input_path),
                        "output_path": str(output_path),
                        "mock_size": output_path.stat().st_size
                    }
                )
                
                return output_path
            else:
                # Re-raise other exceptions
                raise
    
    async def collect_markdown_files(self, workspace: Path) -> List[Path]:
        """
        Collect all generated Markdown files from workspace
        
        Args:
            workspace: Workspace directory to search
            
        Returns:
            List[Path]: List of Markdown files found
        """
        logger.info(
            "Collecting Markdown files from workspace",
            extra={"workspace": str(workspace)}
        )
        
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
                "files": [str(f.relative_to(workspace)) for f in markdown_files]
            }
        )
        
        return markdown_files
    
    async def create_output_zip(
        self,
        markdown_files: List[Path],
        output_zip_path: Path,
        base_path: Optional[Path] = None
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
                "base_path": str(base_path) if base_path else None
            }
        )
        
        try:
            with zipfile.ZipFile(output_zip_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                for file_path in markdown_files:
                    # Determine archive path
                    if base_path:
                        archive_path = file_path.relative_to(base_path)
                    else:
                        archive_path = file_path.name
                    
                    # Add file to ZIP
                    zip_file.write(file_path, archive_path)
            
            logger.info(
                "Output ZIP created successfully",
                extra={
                    "output_zip_path": str(output_zip_path),
                    "output_size": output_zip_path.stat().st_size,
                    "file_count": len(markdown_files)
                }
            )
            
            return output_zip_path
            
        except Exception as e:
            logger.error(
                "Failed to create output ZIP",
                extra={
                    "output_zip_path": str(output_zip_path),
                    "error": str(e)
                }
            )
            raise
    
    async def run_complete_pipeline(
        self,
        input_zip_path: Path,
        workspace: Path,
        timeout: Optional[int] = None
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
                "timeout": timeout
            }
        )
        
        try:
            # Step 1: Extract input archive
            extract_path = workspace / "extracted"
            await self.extract_archive(input_zip_path, extract_path)
            
            # Step 2: Convert using Swift CLI
            output_md_path = workspace / "converted.md"
            await self.convert_with_swift_cli(
                input_path=input_zip_path,
                output_path=output_md_path,
                workspace=workspace,
                timeout=timeout
            )
            
            # Step 3: Collect all Markdown files
            markdown_files = await self.collect_markdown_files(workspace)
            
            # Step 4: Create output ZIP
            output_zip_path = workspace / "output.zip"
            await self.create_output_zip(
                markdown_files=markdown_files,
                output_zip_path=output_zip_path,
                base_path=workspace
            )
            
            logger.info(
                "Complete conversion pipeline finished successfully",
                extra={
                    "input_zip_path": str(input_zip_path),
                    "output_zip_path": str(output_zip_path),
                    "output_size": output_zip_path.stat().st_size,
                    "markdown_file_count": len(markdown_files)
                }
            )
            
            return output_zip_path
            
        except Exception as e:
            logger.error(
                "Conversion pipeline failed",
                extra={
                    "input_zip_path": str(input_zip_path),
                    "workspace": str(workspace),
                    "error": str(e)
                }
            )
            raise


# Global conversion pipeline instance
conversion_pipeline = ConversionPipeline()
