"""
Execution dispatch layer for document processing.

This is the ONLY place that knows about FastAPI's BackgroundTasks.
Routes call schedule_document_processing() instead of calling
background_tasks.add_task() directly — so replacing BackgroundTasks
with Celery (or anything else) later means changing only this file's
body. DocumentProcessingService.run() already takes nothing but a
document ID, so it works unchanged as a Celery task body too.
"""

import uuid

from fastapi import BackgroundTasks

from app.services.document_processing_service import DocumentProcessingService


def schedule_document_processing(background_tasks: BackgroundTasks, document_id: uuid.UUID) -> None:
    background_tasks.add_task(DocumentProcessingService.run, document_id)
