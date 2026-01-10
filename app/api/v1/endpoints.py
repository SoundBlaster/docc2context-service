"""API v1 endpoints implementation"""

from pathlib import Path
from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse

from app.core.logging import get_logger
from app.services.file_validation import validate_upload_file
from app.services.workspace_manager import workspace_manager

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
        JSON response with conversion status
        
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
            
            # TODO: In future tasks, this will:
            # 1. Extract ZIP file in workspace
            # 2. Run Swift CLI conversion in workspace
            # 3. Package results and return
            
            return JSONResponse(
                status_code=200,
                content={
                    "status": "accepted",
                    "message": "File validation and storage successful. Conversion not yet implemented.",
                    "filename": safe_filename,
                    "file_size": len(content),
                    "workspace_id": workspace.name
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
