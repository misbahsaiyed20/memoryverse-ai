"""PDF text extraction via PyMuPDF (fitz)."""

import fitz

from app.processors.base import BaseDocumentProcessor
from app.processors.exceptions import DocumentProcessingError


class PDFProcessor(BaseDocumentProcessor):
    def extract_text(self, file_path: str) -> str:
        try:
            document = fitz.open(file_path)
        except Exception as exc:
            raise DocumentProcessingError(f"Could not open PDF file: {exc}") from exc

        try:
            if document.page_count == 0:
                raise DocumentProcessingError("PDF contains no pages.")
            pages = [page.get_text() for page in document]
        except DocumentProcessingError:
            raise
        except Exception as exc:
            raise DocumentProcessingError(f"Failed to extract text from PDF: {exc}") from exc
        finally:
            document.close()

        return "\n\n".join(pages)
