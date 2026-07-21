"""Validation helpers for document uploads. Reject before anything is saved."""

import re
from pathlib import PurePosixPath

from fastapi import HTTPException, status

ALLOWED_EXTENSIONS = {"pdf", "doc", "docx", "txt", "png", "jpg", "jpeg"}

ALLOWED_MIME_TYPES: dict[str, set[str]] = {
    "pdf": {"application/pdf"},
    "doc": {"application/msword"},
    "docx": {"application/vnd.openxmlformats-officedocument.wordprocessingml.document"},
    "txt": {"text/plain"},
    "png": {"image/png"},
    "jpg": {"image/jpeg"},
    "jpeg": {"image/jpeg"},
}

MAX_FILE_SIZE_BYTES = 25 * 1024 * 1024  # 25 MB


def sanitize_filename(filename: str) -> str:
    """Strip any directory components and unsafe characters."""
    name = PurePosixPath(filename).name
    name = re.sub(r"[^A-Za-z0-9._-]", "_", name)
    return name[:255] or "unnamed"


def get_extension(filename: str) -> str:
    if "." not in filename:
        return ""
    return filename.rsplit(".", 1)[-1].lower()


def validate_extension(extension: str) -> None:
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type: .{extension or 'unknown'}. "
            f"Allowed types: {', '.join(sorted(ALLOWED_EXTENSIONS))}.",
        )


def validate_mime_type(mime_type: str, extension: str) -> None:
    allowed = ALLOWED_MIME_TYPES.get(extension, set())
    if mime_type not in allowed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File content doesn't match its .{extension} extension.",
        )


def validate_size(content: bytes) -> None:
    if len(content) == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded file is empty.")
    if len(content) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File exceeds the 25 MB size limit.",
        )
