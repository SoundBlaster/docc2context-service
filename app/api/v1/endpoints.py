"""API v1 endpoints implementation"""

import time

from fastapi import APIRouter, File, HTTPException, Query, Request, UploadFile
from fastapi.responses import JSONResponse

from app.core.logging import StructuredLogger, get_logger, set_request_id
from app.services.conversion_pipeline import conversion_pipeline
from app.services.file_validation import validate_upload_file
from app.services.health_service import health_service
from app.services.workspace_manager import workspace_manager

logger = get_logger(__name__)
structured_logger = StructuredLogger(__name__)

# Create router for endpoints
router = APIRouter()


@router.get("/health")
async def health_check(
    include_system: bool = Query(False, description="Include optional system checks")
):
    """
    Health check endpoint

    Returns system health status including Swift CLI binary detection.
    Optional system checks can be enabled with query parameter.

    Args:
        include_system: Whether to include disk space and memory checks

    Returns:
        JSON response with health status

    Example:
        Basic health check:
        ```bash
        curl http://localhost:8000/api/v1/health
        ```

        Response:
        ```json
        {
            "status": "ready",
            "binary_detected": true
        }
        ```

        With system checks:
        ```bash
        curl "http://localhost:8000/api/v1/health?include_system=true"
        ```
    """
    try:
        health_status = await health_service.get_health_status(include_system_checks=include_system)

        logger.info(
            "Health check completed",
            extra={
                "overall_status": health_status["status"],
                "binary_detected": health_status["binary_detected"],
                "include_system": include_system,
            },
        )

        return JSONResponse(status_code=200, content=health_status)

    except Exception as e:
        logger.error(
            "Health check failed", extra={"include_system": include_system, "error": str(e)}
        )
        raise HTTPException(status_code=500, detail="Health check failed")


@router.post("/convert")
async def convert_file(file: UploadFile = File(...), request: Request = None):
    """
    Convert DocC archive to Markdown

    Upload a DocC archive (.doccarchive) for conversion to Markdown format.
    The file must be a valid ZIP archive under 100MB.

    Args:
        file: The DocC archive file to convert
        request: Request object for extracting headers

    Returns:
        StreamingResponse: ZIP file containing converted Markdown content
        JSONResponse: Error response with details

    Raises:
        HTTPException: For validation errors or processing failures

    Example:
        Using cURL:
        ```bash
        curl -X POST http://localhost:8000/api/v1/convert \
          -F "file=@/path/to/archive.doccarchive.zip" \
          --output converted.zip
        ```

        Success Response (200):
        - Binary ZIP file download
        - Content-Type: application/zip
        - Content-Disposition: attachment; filename="archive_converted.zip"

        Error Responses:
        - 400: Invalid file type or corrupted ZIP
        - 413: File size exceeds 100MB limit
        - 500: Conversion failed (includes CLI stderr for debugging)
    """
    # Set request ID for tracing
    request_id = request.headers.get("X-Request-ID") if request else None
    set_request_id(request_id)

    extraction_start_time = time.time()
    file_size = 0

    async with workspace_manager.create_workspace() as workspace:
        try:
            logger.info(
                "File upload received",
                extra={
                    "upload_filename": file.filename,
                    "content_type": file.content_type,
                    "workspace_path": str(workspace),
                },
            )

            # Validate the uploaded file
            content, safe_filename = await validate_upload_file(file)
            file_size = len(content)

            # Store the file in the workspace
            file_path = workspace_manager.get_file_path(workspace, safe_filename)

            with open(file_path, "wb") as f:
                f.write(content)

            logger.info(
                "File stored in workspace",
                extra={
                    "safe_filename": safe_filename,
                    "file_path": str(file_path),
                    "file_size": file_size,
                    "workspace_path": str(workspace),
                },
            )

            # Run complete conversion pipeline
            try:
                output_zip_path = await conversion_pipeline.run_complete_pipeline(
                    input_zip_path=file_path, workspace=workspace
                )

                # Read the ZIP content before workspace cleanup
                with open(output_zip_path, "rb") as zip_file:
                    zip_content = zip_file.read()

                # Log successful extraction (Task 5.3)
                extraction_time = time.time() - extraction_start_time
                structured_logger.log_extraction(
                    status="success",
                    file_name=safe_filename,
                    file_size=file_size,
                    extraction_time=extraction_time,
                    request_id=request_id,
                )

                # Create streaming response with ZIP content
                zip_filename = safe_filename.replace(".zip", "_converted.zip")

                from fastapi.responses import Response

                return Response(
                    content=zip_content,
                    media_type="application/zip",
                    headers={"Content-Disposition": f'attachment; filename="{zip_filename}"'},
                )

            except Exception as conversion_error:
                # Handle conversion errors gracefully
                error_message = str(conversion_error)
                extraction_time = time.time() - extraction_start_time

                # Log failed extraction (Task 5.3)
                structured_logger.log_extraction(
                    status="failure",
                    file_name=file.filename,
                    file_size=file_size,
                    extraction_time=extraction_time,
                    error_msg=error_message,
                    request_id=request_id,
                )

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
                            "full_error": error_message,
                        },
                    )
                    raise HTTPException(status_code=500, detail=f"Conversion failed: {cli_stderr}")
                else:
                    # Other conversion errors
                    logger.error(
                        "Conversion pipeline failed",
                        extra={
                            "upload_filename": file.filename,
                            "workspace_path": str(workspace),
                            "error": error_message,
                        },
                    )
                    raise HTTPException(
                        status_code=500, detail=f"Conversion failed: {error_message}"
                    )

        except HTTPException:
            # Re-raise HTTP exceptions (validation errors, conversion errors)
            raise
        except Exception as e:
            # Log unexpected error (Task 5.3)
            extraction_time = time.time() - extraction_start_time
            structured_logger.log_extraction(
                status="failure",
                file_name=file.filename,
                file_size=file_size,
                extraction_time=extraction_time,
                error_msg=str(e),
                request_id=request_id,
            )

            logger.error(
                "Unexpected error in convert endpoint",
                extra={
                    "upload_filename": file.filename,
                    "workspace_path": str(workspace),
                    "error": str(e),
                },
            )
            raise HTTPException(
                status_code=500, detail="Internal server error during file processing"
            )
