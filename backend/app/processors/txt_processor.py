"""Plain-text extraction using the standard library."""

from app.processors.base import BaseDocumentProcessor
from app.processors.exceptions import DocumentProcessingError


class TXTProcessor(BaseDocumentProcessor):
    def extract_text(self, file_path: str) -> str:
        try:
            with open(file_path, "rb") as f:
                raw_bytes = f.read()
        except OSError as exc:
            raise DocumentProcessingError(f"Could not read text file: {exc}") from exc

        # Best-effort UTF-8 decoding — replace anything that doesn't decode
        # cleanly rather than failing the whole extraction over one bad byte.
        return raw_bytes.decode("utf-8", errors="replace")
