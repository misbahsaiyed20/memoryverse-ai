"""
Paragraph-aware chunk generator.

Splits normalized text into overlapping chunks, preferring boundaries in
this order: paragraph, sentence, whitespace, forced split (only if the
whole window has no boundary at all — effectively never, for real text).

Python string slicing operates on Unicode codepoints, not bytes, so it
never splits a single codepoint — that part of "never split unicode
characters" is automatic. Word-splitting is avoided by construction: the
whitespace-boundary fallback searches the *entire* window before falling
back further, so a forced mid-word cut only happens if a stretch longer
than the max chunk size contains no whitespace at all (e.g. one giant
token) — the documented "forced split only when necessary" case.

Pure function of text in, ChunkData out — no database, no I/O, fully
reusable by any future processing pipeline.
"""

from app.chunking.chunk_models import ChunkData
from app.chunking.tokenizer import estimate_tokens

TARGET_CHUNK_SIZE = 1000
MAX_CHUNK_SIZE = 1200
CHUNK_OVERLAP = 150

# Floor below which we won't accept an early boundary — avoids
# pathologically tiny chunks when a paragraph break happens to fall
# right after the start of a window. Not specified in the brief;
# a defensive assumption.
MIN_CHUNK_SIZE = 200

# How far to look ahead for a clean word boundary when repositioning the
# start of an overlapping chunk.
BOUNDARY_SNAP_LOOKAHEAD = 50

_SENTENCE_BREAKS = (". ", "! ", "? ", ".\n", "!\n", "?\n")


class ChunkGenerator:
    @staticmethod
    def generate(text: str) -> list[ChunkData]:
        if not text:
            return []

        chunks: list[ChunkData] = []
        start = 0
        text_length = len(text)
        chunk_index = 0

        while start < text_length:
            remaining = text_length - start
            if remaining <= MAX_CHUNK_SIZE:
                end = text_length
            else:
                end = ChunkGenerator._find_split_point(text, start)

            content = text[start:end]
            chunks.append(
                ChunkData(
                    chunk_index=chunk_index,
                    content=content,
                    start_offset=start,
                    end_offset=end,
                    character_count=len(content),
                    estimated_token_count=estimate_tokens(len(content)),
                )
            )
            chunk_index += 1

            if end >= text_length:
                break

            next_start = ChunkGenerator._snap_forward(text, end - CHUNK_OVERLAP)
            start = max(next_start, start + 1)  # guarantee forward progress

        return chunks

    @staticmethod
    def _find_split_point(text: str, start: int) -> int:
        window_end = min(start + MAX_CHUNK_SIZE, len(text))
        min_end = start + MIN_CHUNK_SIZE

        # 1. Paragraph boundary
        idx = text.rfind("\n\n", start, window_end)
        if idx != -1 and idx + 2 >= min_end:
            return idx + 2

        # 2. Sentence boundary
        for punct in _SENTENCE_BREAKS:
            idx = text.rfind(punct, start, window_end)
            if idx != -1 and idx + len(punct) >= min_end:
                return idx + len(punct)

        # 3. Whitespace boundary
        idx = text.rfind(" ", start, window_end)
        if idx != -1 and idx + 1 >= min_end:
            return idx + 1
        idx = text.rfind("\n", start, window_end)
        if idx != -1 and idx + 1 >= min_end:
            return idx + 1

        # 4. Forced split — only reached if the entire window contains no
        # whitespace at all. Still codepoint-safe by construction.
        return window_end

    @staticmethod
    def _snap_forward(text: str, pos: int) -> int:
        """Nudge pos forward to the next whitespace boundary so an
        overlapping chunk doesn't start mid-word. Falls back to pos
        unchanged if nothing found within the lookahead window."""
        pos = max(pos, 0)
        limit = min(pos + BOUNDARY_SNAP_LOOKAHEAD, len(text))
        for i in range(pos, limit):
            if text[i].isspace():
                return i + 1
        return pos
