"""
Base document processor.

Every processor implements this one contract: read a file, return its
text. Processors must NOT touch the database, change document status,
know about users, or know about AI/chunking — that orchestration lives
entirely in DocumentProcessingService.
"""

from abc import ABC, abstractmethod


class BaseDocumentProcessor(ABC):
    @abstractmethod
    def extract_text(self, file_path: str) -> str:
        """Read the file at file_path and return its extracted text.

        Raises DocumentProcessingError (or a subclass) if the file can't
        be read or parsed.
        """
        raise NotImplementedError
