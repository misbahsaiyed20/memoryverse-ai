"""
Processor factory.

Selects the right processor by file extension via a registry — adding a
future processor (OCR, HTML, images, ...) means adding one line here,
never touching DocumentProcessingService.
"""

from app.processors.base import BaseDocumentProcessor
from app.processors.docx_processor import DOCXProcessor
from app.processors.exceptions import UnsupportedDocumentTypeError
from app.processors.pdf_processor import PDFProcessor
from app.processors.txt_processor import TXTProcessor

_PROCESSOR_REGISTRY: dict[str, type[BaseDocumentProcessor]] = {
    "pdf": PDFProcessor,
    "docx": DOCXProcessor,
    "txt": TXTProcessor,
}


class ProcessorFactory:
    @staticmethod
    def get_processor(file_extension: str) -> BaseDocumentProcessor:
        processor_cls = _PROCESSOR_REGISTRY.get(file_extension.lower())
        if processor_cls is None:
            raise UnsupportedDocumentTypeError(
                f"No processor registered for file type: .{file_extension}"
            )
        return processor_cls()
