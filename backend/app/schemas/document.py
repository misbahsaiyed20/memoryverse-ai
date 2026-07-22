"""
Document schemas.

DocumentOut deliberately excludes storage_path and stored_filename —
"never expose storage paths" is a stated security requirement, and the
client never needs either: downloads go through /documents/{id}/download,
not a direct path.

It also excludes the raw extracted_text (Sprint 4 requirement: "Do not
return the full extracted text in Sprint 4 responses") — only whether
extraction has happened (has_extracted_text) is exposed. Because that's
a derived value with no matching ORM attribute, routes build DocumentOut
via from_document() rather than model_validate(), which would otherwise
fail looking for a has_extracted_text attribute on the Document object.
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.document import Document, DocumentStatus


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

    # Sprint 4
    processed_at: datetime | None
    has_extracted_text: bool
    processing_error: str | None

    @classmethod
    def from_document(cls, document: Document) -> "DocumentOut":
        return cls(
            id=document.id,
            title=document.title,
            original_filename=document.original_filename,
            file_extension=document.file_extension,
            mime_type=document.mime_type,
            file_size=document.file_size,
            status=document.status,
            created_at=document.created_at,
            updated_at=document.updated_at,
            processed_at=document.processed_at,
            has_extracted_text=document.extracted_text is not None,
            processing_error=document.processing_error,
        )


class DocumentRenameRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
