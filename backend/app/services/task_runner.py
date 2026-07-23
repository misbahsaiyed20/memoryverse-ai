"""
Execution dispatch layer for document processing and chunking.

This is the ONLY place that knows about FastAPI's BackgroundTasks.
Routes call schedule_document_processing() / schedule_document_chunking()
instead of calling background_tasks.add_task() directly — so replacing
BackgroundTasks with Celery (or anything else) later means changing only
this file's body. Both service .run() methods already take nothing but
a document ID, so they work unchanged as Celery task bodies too.
"""

import uuid

from fastapi import BackgroundTasks

from app.services.chunking_service import ChunkingService
from app.services.document_processing_service import DocumentProcessingService


def schedule_document_processing(background_tasks: BackgroundTasks, document_id: uuid.UUID) -> None:
    background_tasks.add_task(DocumentProcessingService.run, document_id)


def schedule_document_chunking(background_tasks: BackgroundTasks, document_id: uuid.UUID) -> None:
    background_tasks.add_task(ChunkingService.run, document_id)
