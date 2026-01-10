"""Response streaming service for efficient file delivery"""

import os
import zipfile
from pathlib import Path
from typing import AsyncGenerator, Optional

from fastapi.responses import StreamingResponse

from app.core.logging import get_logger

logger = get_logger(__name__)


class ResponseStreamer:
    """Handles streaming responses for large files"""
    
    def __init__(self):
        self.chunk_size = 8192  # 8KB chunks for streaming
    
    async def stream_file(self, file_path: Path) -> AsyncGenerator[bytes, None]:
        """
        Stream a file in chunks
        
        Args:
            file_path: Path to file to stream
            
        Yields:
            bytes: File content chunks
        """
        logger.info(
            "Starting file stream",
            extra={
                "file_path": str(file_path),
                "file_size": file_path.stat().st_size,
                "chunk_size": self.chunk_size
            }
        )
        
        try:
            with open(file_path, 'rb') as file:
                while True:
                    chunk = file.read(self.chunk_size)
                    if not chunk:
                        break
                    yield chunk
            
            logger.info(
                "File stream completed",
                extra={
                    "file_path": str(file_path),
                    "total_bytes": file_path.stat().st_size
                }
            )
            
        except Exception as e:
            logger.error(
                "File streaming failed",
                extra={
                    "file_path": str(file_path),
                    "error": str(e)
                }
            )
            raise
    
    async def stream_zip_on_the_fly(
        self,
        files_to_zip: list[tuple[Path, str]],  # (file_path, archive_name)
        compression: int = zipfile.ZIP_DEFLATED
    ) -> AsyncGenerator[bytes, None]:
        """
        Stream a ZIP file created on-the-fly
        
        Args:
            files_to_zip: List of (file_path, archive_name) tuples
            compression: ZIP compression level
            
        Yields:
            bytes: ZIP content chunks
        """
        logger.info(
            "Starting on-the-fly ZIP stream",
            extra={
                "file_count": len(files_to_zip),
                "compression": compression,
                "chunk_size": self.chunk_size
            }
        )
        
        try:
            # Create ZIP in memory with streaming
            import io
            
            zip_buffer = io.BytesIO()
            
            with zipfile.ZipFile(zip_buffer, 'w', compression) as zip_file:
                for file_path, archive_name in files_to_zip:
                    logger.debug(
                        "Adding file to ZIP stream",
                        extra={
                            "file_path": str(file_path),
                            "archive_name": archive_name,
                            "file_size": file_path.stat().st_size
                        }
                    )
                    
                    zip_file.write(file_path, archive_name)
            
            # Stream the ZIP content
            zip_content = zip_buffer.getvalue()
            total_size = len(zip_content)
            
            logger.info(
                "ZIP stream created, starting to stream content",
                extra={
                    "total_size": total_size,
                    "file_count": len(files_to_zip)
                }
            )
            
            # Stream in chunks
            for i in range(0, total_size, self.chunk_size):
                chunk = zip_content[i:i + self.chunk_size]
                yield chunk
            
            logger.info(
                "ZIP stream completed",
                extra={
                    "total_bytes": total_size,
                    "chunks_sent": (total_size + self.chunk_size - 1) // self.chunk_size
                }
            )
            
        except Exception as e:
            logger.error(
                "ZIP streaming failed",
                extra={
                    "file_count": len(files_to_zip),
                    "error": str(e)
                }
            )
            raise
    
    def create_streaming_response(
        self,
        file_path: Path,
        filename: Optional[str] = None,
        media_type: str = "application/octet-stream"
    ) -> StreamingResponse:
        """
        Create a streaming response for a file
        
        Args:
            file_path: Path to file to stream
            filename: Filename for Content-Disposition header
            media_type: Media type for Content-Type header
            
        Returns:
            StreamingResponse: Configured streaming response
        """
        if filename is None:
            filename = file_path.name
        
        headers = {
            "Content-Disposition": f"attachment; filename=\"{filename}\""
        }
        
        logger.info(
            "Creating streaming response",
            extra={
                "file_path": str(file_path),
                "response_filename": filename,
                "media_type": media_type,
                "file_size": file_path.stat().st_size
            }
        )
        
        return StreamingResponse(
            self.stream_file(file_path),
            media_type=media_type,
            headers=headers
        )
    
    def create_zip_streaming_response(
        self,
        files_to_zip: list[tuple[Path, str]],
        zip_filename: str = "converted.zip",
        media_type: str = "application/zip"
    ) -> StreamingResponse:
        """
        Create a streaming response for on-the-fly ZIP
        
        Args:
            files_to_zip: List of (file_path, archive_name) tuples
            zip_filename: Filename for the ZIP
            media_type: Media type for Content-Type header
            
        Returns:
            StreamingResponse: Configured ZIP streaming response
        """
        headers = {
            "Content-Disposition": f"attachment; filename=\"{zip_filename}\""
        }
        
        logger.info(
            "Creating ZIP streaming response",
            extra={
                "zip_filename": zip_filename,
                "media_type": media_type,
                "file_count": len(files_to_zip)
            }
        )
        
        return StreamingResponse(
            self.stream_zip_on_the_fly(files_to_zip),
            media_type=media_type,
            headers=headers
        )


# Global response streamer instance
response_streamer = ResponseStreamer()
