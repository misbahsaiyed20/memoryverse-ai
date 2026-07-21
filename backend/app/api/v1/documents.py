"""Document management routes — upload, list, rename, delete, download."""

import uuid

from fastapi import APIRouter, Depends, File, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_storage_service
from app.db.session import get_db
from app.models.user import User
from app.schemas.document import DocumentOut, DocumentRenameRequest
from app.services.document_service import DocumentService
from app.services.storage.base import StorageService
from app.utils.response import success_response

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    storage: StorageService = Depends(get_storage_service),
):
    service = DocumentService(db)
    document = await service.upload(current_user.id, file, storage)
    return success_response(
        DocumentOut.model_validate(document).model_dump(mode="json"),
        "Document uploaded successfully.",
    )


@router.get("")
def list_documents(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = DocumentService(db)
    documents = service.list_for_user(current_user.id)
    return success_response(
        [DocumentOut.model_validate(d).model_dump(mode="json") for d in documents],
        "Documents retrieved successfully.",
    )


@router.get("/{document_id}")
def get_document(
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = DocumentService(db)
    document = service.get_owned_or_404(document_id, current_user.id)
    return success_response(
        DocumentOut.model_validate(document).model_dump(mode="json"),
        "Document retrieved successfully.",
    )


@router.patch("/{document_id}")
def rename_document(
    document_id: uuid.UUID,
    body: DocumentRenameRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = DocumentService(db)
    document = service.get_owned_or_404(document_id, current_user.id)
    updated = service.rename(document, body.title)
    return success_response(
        DocumentOut.model_validate(updated).model_dump(mode="json"),
        "Document renamed successfully.",
    )


@router.delete("/{document_id}")
def delete_document(
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    storage: StorageService = Depends(get_storage_service),
):
    service = DocumentService(db)
    document = service.get_owned_or_404(document_id, current_user.id)
    service.delete(document, storage)
    return success_response(None, "Document deleted successfully.")


@router.get("/{document_id}/download")
def download_document(
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    storage: StorageService = Depends(get_storage_service),
):
    service = DocumentService(db)
    document = service.get_owned_or_404(document_id, current_user.id)
    file_obj = storage.get(document.storage_path)

    def iterfile():
        try:
            while chunk := file_obj.read(65536):
                yield chunk
        finally:
            file_obj.close()

    return StreamingResponse(
        iterfile(),
        media_type=document.mime_type,
        headers={"Content-Disposition": f'attachment; filename="{document.original_filename}"'},
    )
