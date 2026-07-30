"""Document management routes — upload, list, rename, delete, download, process."""

import uuid

from fastapi import APIRouter, BackgroundTasks, Depends, File, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_storage_service
from app.db.session import get_db
from app.models.user import User
from app.schemas.document import DocumentOut, DocumentRenameRequest
from app.services.chunking_service import ChunkingService
from app.services.document_processing_service import DocumentProcessingService
from app.services.document_service import DocumentService
from app.services.extraction_service import ExtractionService
from app.services.storage.base import StorageService
from app.services.task_runner import schedule_document_chunking, schedule_document_processing
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
        DocumentOut.from_document(document).model_dump(mode="json"),
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
        [DocumentOut.from_document(d).model_dump(mode="json") for d in documents],
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
        DocumentOut.from_document(document).model_dump(mode="json"),
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
        DocumentOut.from_document(updated).model_dump(mode="json"),
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


@router.post("/{document_id}/process")
def process_document(
    document_id: uuid.UUID,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Starts background text extraction. Returns once status flips to
    PROCESSING — the actual extraction happens after this response is sent.
    """
    service = DocumentProcessingService(db)
    document = service.mark_processing(document_id, current_user.id)
    schedule_document_processing(background_tasks, document_id)
    return success_response(
        {"status": document.status.value},
        "Document processing started.",
    )


@router.post("/{document_id}/chunk")
def chunk_document(
    document_id: uuid.UUID,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Starts background chunk generation. Chunking is independent of
    processing — it only runs when explicitly triggered here, never
    automatically after /process completes.
    """
    service = ChunkingService(db)
    service.validate_for_chunking(document_id, current_user.id)
    schedule_document_chunking(background_tasks, document_id)
    return success_response(
        {"document_id": str(document_id), "chunking_status": "started"},
        "Chunking started.",
    )

@router.post("/{document_id}/extract")
def extract_document(
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Extracts structured entities (skills, projects, certifications,
    etc.) from this document's chunks and persists them as KnowledgeNode
    rows. Unlike /process and /chunk, this runs synchronously and
    returns the real count once extraction finishes — there is no
    "started" response, because nodes_created can't be known until the
    work is done. For a large document this means a slower response,
    not a background job; see ExtractionService's docstring for why.
    """
    service = ExtractionService(db)
    document = service.validate_for_extraction(document_id, current_user.id)
    summary = service.run(document)
    return success_response(
        {"nodes_created": summary.nodes_created, "edges_created": summary.edges_created},
        "Extraction completed successfully.",
    )