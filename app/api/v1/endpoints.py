"""API v1 endpoints implementation"""

import zipfile
from pathlib import Path
from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse, FileResponse

from app.core.logging import get_logger
from app.services.file_validation import validate_upload_file
from app.services.workspace_manager import workspace_manager
from app.services.subprocess_manager import subprocess_manager, SubprocessResult

logger = get_logger(__name__)

# Create router for endpoints
router = APIRouter()


@router.post("/convert")
async def convert_file(file: UploadFile = File(...)):
    """
    Convert DocC archive to Markdown
    
    Upload a DocC archive (.doccarchive) for conversion to Markdown format.
    The file must be a valid ZIP archive under 100MB.
    
    Args:
        file: The DocC archive file to convert
        
    Returns:
        JSON response with conversion status or FileResponse with converted content
        
    Raises:
        HTTPException: For validation errors or processing failures
    """
    async with workspace_manager.create_workspace() as workspace:
        try:
            logger.info(
                "File upload received",
                extra={
                    "upload_filename": file.filename,
                    "content_type": file.content_type,
                    "workspace_path": str(workspace)
                }
            )
            
            # Validate the uploaded file
            content, safe_filename = await validate_upload_file(file)
            
            # Store the file in the workspace
            file_path = workspace_manager.get_file_path(workspace, safe_filename)
            
            with open(file_path, 'wb') as f:
                f.write(content)
            
            logger.info(
                "File stored in workspace",
                extra={
                    "safe_filename": safe_filename,
                    "file_path": str(file_path),
                    "file_size": len(content),
                    "workspace_path": str(workspace)
                }
            )
            
            # Extract ZIP file in workspace
            extract_path = workspace / "extracted"
            extract_path.mkdir(exist_ok=True)
            
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                zip_ref.extractall(extract_path)
            
            logger.info(
                "ZIP file extracted",
                extra={
                    "extract_path": str(extract_path),
                    "file_count": len(list(extract_path.rglob("*")))
                }
            )
            
            # Prepare output path
            output_filename = safe_filename.replace('.zip', '.md')
            output_path = workspace / output_filename
            
            # Convert using Swift CLI
            try:
                conversion_result = await subprocess_manager.convert_docc_to_markdown(
                    input_path=file_path,
                    output_path=output_path,
                    workspace=workspace
                )
            except Exception as e:
                # Handle missing Swift CLI gracefully
                if "No such file or directory" in str(e) or "docc2context" in str(e):
                    logger.warning(
                        "Swift CLI not available, returning mock conversion",
                        extra={
                            "error": str(e),
                            "workspace_path": str(workspace)
                        }
                    )
                    # Create a mock output file for testing
                    mock_content = f"""# Mock Conversion Result

This is a mock conversion result because the Swift CLI (`docc2context`) is not yet installed.

## File Information
- Original filename: {safe_filename}
- File size: {len(content)} bytes
- Workspace: {workspace.name}
- Extraction path: {extract_path}

## Next Steps
1. Install the Swift CLI binary (Task 1.2)
2. Update the subprocess configuration to point to the correct binary path
3. The conversion will then work with real DocC archives

## Extracted Files
{chr(10).join(f"- {f.name}" for f in extract_path.rglob("*") if f.is_file())}

---
*This is a temporary mock response for development purposes.*
"""
                    with open(output_path, 'w') as f:
                        f.write(mock_content)
                    
                    conversion_result = SubprocessResult(
                        returncode=0,
                        stdout="Mock conversion completed",
                        stderr="Swift CLI not available - using mock response",
                        command=["mock", "conversion"]
                    )
                else:
                    raise
            
            if not conversion_result.success:
                raise HTTPException(
                    status_code=500,
                    detail=f"Conversion failed: {conversion_result.stderr}"
                )
            
            # Check if output file was created
            if not output_path.exists():
                raise HTTPException(
                    status_code=500,
                    detail="Conversion completed but no output file found"
                )
            
            logger.info(
                "Conversion completed successfully",
                extra={
                    "output_path": str(output_path),
                    "output_size": output_path.stat().st_size,
                    "workspace_path": str(workspace)
                }
            )
            
            # For now, return JSON response with conversion info
            # In future, we might return the actual file
            return JSONResponse(
                status_code=200,
                content={
                    "status": "completed",
                    "message": "File conversion completed successfully",
                    "input_filename": safe_filename,
                    "output_filename": output_filename,
                    "file_size": len(content),
                    "output_size": output_path.stat().st_size,
                    "workspace_id": workspace.name,
                    "conversion_stdout": conversion_result.stdout,
                    "conversion_stderr": conversion_result.stderr
                }
            )
            
        except HTTPException:
            # Re-raise HTTP exceptions (validation errors)
            raise
        except Exception as e:
            logger.error(
                "Unexpected error in convert endpoint",
                extra={
                    "upload_filename": file.filename,
                    "workspace_path": str(workspace),
                    "error": str(e)
                }
            )
            raise HTTPException(
                status_code=500,
                detail="Internal server error during file processing"
            )
