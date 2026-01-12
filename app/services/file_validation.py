"""File validation service for upload security"""

import io
import os
import zipfile

from fastapi import HTTPException, UploadFile

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# ZIP file magic numbers
ZIP_MAGIC_NUMBERS = [
    b"PK\x03\x04",  # Local file header
    b"PK\x05\x06",  # End of central directory
    b"PK\x07\x08",  # Spanned archive
]

# Safe filename characters (alphanumeric, dash, underscore, period, and common DocC characters)
# DocC archives can contain Swift function signatures and special characters
SAFE_FILENAME_CHARS = set(
    "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_.():![]&<>@#$%^+=,;"
)
MAX_FILENAME_LENGTH = 255


class FileValidationError(Exception):
    """Raised when file validation fails"""

    pass


def validate_file_size(file_size: int) -> None:
    """Validate file size against configured limits"""
    max_size = settings.max_upload_size_mb * 1024 * 1024  # Convert MB to bytes

    if file_size > max_size:
        logger.warning(
            "File size exceeds limit",
            extra={
                "file_size": file_size,
                "max_size": max_size,
                "size_mb": file_size / (1024 * 1024),
                "limit_mb": settings.max_upload_size_mb,
            },
        )
        raise FileValidationError(
            f"File size {file_size / (1024 * 1024):.1f}MB exceeds limit of {settings.max_upload_size_mb}MB"
        )


def validate_zip_magic_number(file_content: bytes) -> None:
    """Validate that file starts with ZIP magic number"""
    if not file_content:
        raise FileValidationError("Empty file provided")

    # Check first few bytes against ZIP magic numbers
    is_zip = any(file_content.startswith(magic) for magic in ZIP_MAGIC_NUMBERS)

    if not is_zip:
        logger.warning(
            "Invalid file type - not a ZIP archive",
            extra={
                "file_header": file_content[:16].hex(),
                "expected_magic": [magic.hex() for magic in ZIP_MAGIC_NUMBERS],
            },
        )
        raise FileValidationError("Invalid file type: only ZIP archives are allowed")


def sanitize_filename(filename: str) -> str:
    """Sanitize filename to prevent path traversal and other attacks"""
    if not filename:
        raise FileValidationError("Empty filename provided")

    # Check for null bytes (path traversal variant)
    if "\x00" in filename:
        logger.error(
            "Null byte detected in filename",
            extra={"original_filename": repr(filename)},
        )
        raise FileValidationError("Filename contains null byte")

    # Check for control characters
    if any(ord(c) < 32 and c not in "\t\n\r" for c in filename):
        logger.warning(
            "Control characters detected in filename",
            extra={"original_filename": repr(filename)},
        )
        raise FileValidationError("Filename contains control characters")

    # Remove path components (handles both / and \)
    filename = os.path.basename(filename)

    # Additional check: ensure no path separators remain
    if "/" in filename or "\\" in filename:
        logger.error(
            "Path separator in filename after basename",
            extra={"original_filename": filename},
        )
        raise FileValidationError("Filename contains path separators")

    # Check filename length
    if len(filename) > MAX_FILENAME_LENGTH:
        raise FileValidationError(f"Filename too long: {len(filename)} > {MAX_FILENAME_LENGTH}")

    # Check for safe characters only
    if not all(c in SAFE_FILENAME_CHARS for c in filename):
        unsafe_chars = set(filename) - SAFE_FILENAME_CHARS
        logger.warning(
            "Filename contains unsafe characters",
            extra={"original_filename": filename, "unsafe_chars": list(unsafe_chars)},
        )
        raise FileValidationError(f"Filename contains unsafe characters: {list(unsafe_chars)}")

    # Prevent hidden files (starting with dot)
    # Allow legitimate extensions like .doccarchive.zip
    # Also allow macOS resource fork files (._filename)
    if filename.startswith("."):
        # Check if it's a hidden file (starts with dot)
        # We want to reject hidden files but allow legitimate extensions
        # A file is considered hidden if:
        # 1. It starts with a dot and has no other dots (like .gitignore)
        # 2. It starts with multiple dots (like ..hiddenfile)
        # 3. It starts with a dot followed by another dot (like .hidden.ext)
        # Exception: Allow macOS resource fork files (._filename)
        parts = filename.split(".")

        # Check if this is a macOS resource fork file (starts with ._ and has extension)
        if len(parts) >= 3 and parts[0] == "" and parts[1].startswith("_"):
            # This is a macOS resource fork file like ._SpecificationCore.doccarchive
            # Allow it if it has a legitimate extension
            return filename

        if (len(parts) > 1 and parts[0] == "" and parts[1] != "") or filename.startswith(".."):
            # This is a hidden file like .gitignore, .bashrc, .hidden.ext
            raise FileValidationError("Hidden filenames not allowed")

    return filename


def validate_zip_bomb_protection(zip_file: zipfile.ZipFile, original_size: int) -> None:
    """Validate ZIP file to prevent zip bomb attacks"""
    total_uncompressed_size = 0
    max_decompressed_size = min(
        original_size * 5,  # 5x compression ratio limit
        settings.max_decompressed_size_mb * 1024 * 1024,  # Hard size limit
    )

    file_count = 0
    max_files = 5000  # Increased limit for DocC archives which can have many files

    for file_info in zip_file.infolist():
        file_count += 1

        # Check file count limit
        if file_count > max_files:
            logger.warning(
                "Too many files in ZIP archive",
                extra={"file_count": file_count, "max_files": max_files},
            )
            raise FileValidationError(
                f"ZIP archive contains too many files: {file_count} > {max_files}"
            )

        # Check for path traversal in file names
        # Don't use sanitize_filename here as it strips paths
        # Instead, validate the path doesn't escape
        if file_info.filename.startswith("/") or file_info.filename.startswith("\\"):
            logger.error(
                "Absolute path detected in ZIP",
                extra={"zip_filename": file_info.filename},
            )
            raise FileValidationError(f"Absolute paths not allowed in ZIP: {file_info.filename}")

        if ".." in file_info.filename:
            logger.error(
                "Path traversal detected in ZIP",
                extra={"zip_filename": file_info.filename},
            )
            raise FileValidationError(f"Path traversal detected in ZIP: {file_info.filename}")

        # Check for null bytes in filename
        if "\x00" in file_info.filename:
            logger.error(
                "Null byte detected in ZIP filename",
                extra={"zip_filename": repr(file_info.filename)},
            )
            raise FileValidationError("Null byte detected in ZIP filename")

        # Check file size
        file_size = file_info.file_size
        total_uncompressed_size += file_size

        if total_uncompressed_size > max_decompressed_size:
            logger.warning(
                "ZIP decompression size exceeds limit",
                extra={
                    "total_size": total_uncompressed_size,
                    "max_size": max_decompressed_size,
                    "total_size_mb": total_uncompressed_size / (1024 * 1024),
                    "limit_mb": max_decompressed_size / (1024 * 1024),
                },
            )
            raise FileValidationError(
                f"ZIP decompression size {total_uncompressed_size / (1024 * 1024):.1f}MB "
                f"exceeds limit of {max_decompressed_size / (1024 * 1024):.1f}MB"
            )

        # Check for encrypted files (potential security risk)
        if file_info.flag_bits & 0x1:  # Bit 0 indicates encryption
            logger.warning(
                "Encrypted file detected in ZIP",
                extra={"zip_filename": file_info.filename, "encrypted": True},
            )
            raise FileValidationError("Encrypted files are not supported")

        # Check for symlinks in ZIP metadata
        # Symlink flag is 0xA000 in the upper 16 bits of external_attr (Unix)
        if (file_info.external_attr >> 16) == 0xA000:
            logger.warning(
                "Symlink detected in ZIP metadata",
                extra={"zip_filename": file_info.filename},
            )
            raise FileValidationError(f"Symlinks not allowed in ZIP: {file_info.filename}")

    logger.info(
        "ZIP bomb protection validation passed",
        extra={
            "original_size": original_size,
            "uncompressed_size": total_uncompressed_size,
            "file_count": file_count,
            "compression_ratio": (
                total_uncompressed_size / original_size if original_size > 0 else 0
            ),
        },
    )


async def validate_upload_file(file: UploadFile) -> tuple[bytes, str]:
    """Comprehensive validation of uploaded file"""
    try:
        # Read file content for validation
        content = await file.read()
        file_size = len(content)

        logger.info(
            "Starting file validation",
            extra={
                "upload_filename": file.filename,
                "content_type": file.content_type,
                "file_size": file_size,
            },
        )

        # Step 1: Validate file size
        validate_file_size(file_size)

        # Step 2: Validate magic number
        validate_zip_magic_number(content)

        # Step 3: Sanitize filename
        safe_filename = sanitize_filename(file.filename or "upload.zip")

        # Step 4: Validate ZIP structure and bomb protection
        try:
            # Use content bytes instead of file object for ZIP validation
            with zipfile.ZipFile(io.BytesIO(content), mode="r") as zip_file:
                validate_zip_bomb_protection(zip_file, file_size)
        except zipfile.BadZipFile as e:
            logger.error(
                "Invalid ZIP file structure",
                extra={"upload_filename": file.filename, "error": str(e)},
            )
            raise FileValidationError(f"Invalid ZIP file: {str(e)}")

        # Reset file pointer for further processing
        await file.seek(0)

        logger.info(
            "File validation completed successfully",
            extra={
                "safe_filename": safe_filename,
                "file_size": file_size,
                "validation_passed": True,
            },
        )

        return content, safe_filename

    except FileValidationError as e:
        logger.warning(
            "File validation failed", extra={"upload_filename": file.filename, "error": str(e)}
        )
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(
            "Unexpected error during file validation",
            extra={"upload_filename": file.filename, "error": str(e)},
        )
        raise HTTPException(status_code=500, detail="Internal server error during file validation")
