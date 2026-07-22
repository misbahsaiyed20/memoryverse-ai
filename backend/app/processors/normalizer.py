"""
Text normalizer.

Cleans up raw extracted text without altering its meaning: consistent
line endings, no trailing whitespace, paragraph boundaries preserved,
excessive blank lines collapsed. Reusable by any future processing
pipeline, not just Sprint 4's.
"""

import re


class TextNormalizer:
    @staticmethod
    def normalize(text: str) -> str:
        # Normalize line endings to \n
        text = text.replace("\r\n", "\n").replace("\r", "\n")

        # Trim trailing whitespace on each line (keeps paragraph structure)
        lines = [line.rstrip() for line in text.split("\n")]
        text = "\n".join(lines)

        # Collapse 3+ consecutive blank lines down to exactly one blank
        # line — preserves paragraph breaks (a single blank line) without
        # letting large gaps accumulate.
        text = re.sub(r"\n{3,}", "\n\n", text)

        return text.strip()
