"""DOCX text extraction via python-docx.

Note: python-docx only reads the modern .docx format, not legacy .doc
files. Sprint 3 allows .doc uploads, but no processor is registered for
it here — ProcessorFactory raises UnsupportedDocumentTypeError for
"doc", which DocumentProcessingService turns into a FAILED status with
a clear message rather than a crash. A dedicated .doc processor (e.g.
via antiword or textract) is future work, not in this sprint's scope.
"""

import docx

from app.processors.base import BaseDocumentProcessor
from app.processors.exceptions import DocumentProcessingError


class DOCXProcessor(BaseDocumentProcessor):
    def extract_text(self, file_path: str) -> str:
        try:
            document = docx.Document(file_path)
        except Exception as exc:
            raise DocumentProcessingError(f"Could not open DOCX file: {exc}") from exc

        try:
            paragraphs = [paragraph.text for paragraph in document.paragraphs]
        except Exception as exc:
            raise DocumentProcessingError(f"Failed to extract text from DOCX: {exc}") from exc

        return "\n".join(paragraphs)
