"""Token estimation.

Deliberately not a real tokenizer — just a cheap character-based
approximation, per Sprint 5 scope ("do not introduce heavy tokenizer
libraries"). Good enough for planning purposes; a real tokenizer
(tiktoken or similar) can replace this later without touching anything
that calls it, since the signature (character count -> int) won't change.
"""

import math


def estimate_tokens(character_count: int) -> int:
    return math.ceil(character_count / 4)
