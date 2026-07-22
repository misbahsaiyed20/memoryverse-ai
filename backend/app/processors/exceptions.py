"""Exceptions raised during document processing.

Processors raise these; DocumentProcessingService catches them centrally
(along with any other unexpected exception) and translates them into a
FAILED status + processing_error message.
"""


class DocumentProcessingError(Exception):
    """Base exception for any document processing failure."""


class UnsupportedDocumentTypeError(DocumentProcessingError):
    """Raised by ProcessorFactory when no processor is registered for a file type."""
