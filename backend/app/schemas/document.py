"""
Document schemas.

DocumentOut deliberately excludes storage_path and stored_filename —
"never expose storage paths" is a stated security requirement, and the
client never needs either: downloads go through /documents/{id}/download,
not a direct path.
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.document import DocumentStatus


class DocumentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    original_filename: str
    file_extension: str
    mime_type: str
    file_size: int
    status: DocumentStatus
    created_at: datetime
    updated_at: datetime


class DocumentRenameRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
