"""
Builds the prompt sent to Gemini for structured information extraction.
"""

from textwrap import dedent


def build_extraction_prompt(text: str) -> str:
    """
    Build the extraction prompt for Gemini.
    Gemini is expected to return structured JSON matching
    GeminiExtractionResult.
    """

    return dedent(
        f"""
        You are MemoryVerse AI.

        Extract structured information from the document.

        Rules:
        - Extract only information explicitly present.
        - Do not invent facts.
        - Do not infer missing information.
        - Every extracted entity must include an evidence_quote copied
          exactly from the source text.
        - Return only valid JSON matching the required schema.

        DOCUMENT:

        {text}
        """
    ).strip()