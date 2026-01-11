"""API v1 endpoints implementation"""

from pathlib import Path
from fastapi import APIRouter, File, UploadFile, HTTPException, Query, Depends
from fastapi.responses import JSONResponse


from app.core.logging import get_logger
from app.services.file_validation import validate_upload_file
from app.services.workspace_manager import workspace_manager
from app.services.conversion_pipeline import conversion_pipeline
from app.services.response_streaming import response_streamer
from app.services.health_service import health_service

logger = get_logger(__name__)

# Create router for endpoints
router = APIRouter()




@router.get("/health")
async def health_check(include_system: bool = Query(False, description="Include optional system checks")):
    """
    Health check endpoint
    
    Returns system health status including Swift CLI binary detection.
    Optional system checks can be enabled with query parameter.
    
    Args:
        include_system: Whether to include disk space and memory checks
        
    Returns:
        JSON response with health status
    """
    try:
        health_status = await health_service.get_health_status(
            include_system_checks=include_system
        )
        
        logger.info(
            "Health check completed",
            extra={
                "overall_status": health_status["status"],
                "binary_detected": health_status["binary_detected"],
                "include_system": include_system
            }
        )
        
        return JSONResponse(
            status_code=200,
            content=health_status
        )
        
    except Exception as e:
        logger.error(
            "Health check failed",
            extra={
                "include_system": include_system,
                "error": str(e)
            }
        )
        raise HTTPException(
            status_code=500,
            detail="Health check failed"
        )


@router.post("/convert")
async def convert_file(file: UploadFile = File(...)):
    """
    Convert DocC archive to Markdown
    
    Upload a DocC archive (.doccarchive) for conversion to Markdown format.
    The file must be a valid ZIP archive under 100MB.
    
    Args:
        file: The DocC archive file to convert
        
    Returns:
        StreamingResponse: ZIP file containing converted Markdown content
        JSONResponse: Error response with details
        
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
            
            # Run complete conversion pipeline
            try:
                output_zip_path = await conversion_pipeline.run_complete_pipeline(
                    input_zip_path=file_path,
                    workspace=workspace
                )
                
                # Read the ZIP content before workspace cleanup
                with open(output_zip_path, 'rb') as zip_file:
                    zip_content = zip_file.read()
                
                # Create streaming response with ZIP content
                zip_filename = safe_filename.replace('.zip', '_converted.zip')
                
                from fastapi.responses import Response
                return Response(
                    content=zip_content,
                    media_type="application/zip",
                    headers={
                        "Content-Disposition": f"attachment; filename=\"{zip_filename}\""
                    }
                )
                
            except Exception as conversion_error:
                # Handle conversion errors gracefully
                error_message = str(conversion_error)
                
                # Check if it's a Swift CLI error
                if "Conversion failed:" in error_message:
                    # Extract CLI stderr for detailed error reporting
                    cli_stderr = error_message.replace("Conversion failed: ", "")
                    logger.error(
                        "Swift CLI conversion failed",
                        extra={
                            "upload_filename": file.filename,
                            "workspace_path": str(workspace),
                            "cli_stderr": cli_stderr,
                            "full_error": error_message
                        }
                    )
                    raise HTTPException(
                        status_code=500,
                        detail=f"Conversion failed: {cli_stderr}"
                    )
                else:
                    # Other conversion errors
                    logger.error(
                        "Conversion pipeline failed",
                        extra={
                            "upload_filename": file.filename,
                            "workspace_path": str(workspace),
                            "error": error_message
                        }
                    )
                    raise HTTPException(
                        status_code=500,
                        detail=f"Conversion failed: {error_message}"
                    )
            
        except HTTPException:
            # Re-raise HTTP exceptions (validation errors, conversion errors)
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
