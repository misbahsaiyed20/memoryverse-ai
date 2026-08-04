"""
Thin wrapper around the Gemini SDK — the only file in this codebase that
imports google.genai. Owns retry/backoff for transient failures and
malformed output.

Two entry points:
- extract_from_text() — structured JSON extraction (Sprint 6), used by
  ExtractionService. Unchanged by Sprint 8 Part 3.
- generate_text() — free-text generation (Sprint 8 Part 3), used by
  VerseAIService for RAG answers. Added here rather than in a new file
  specifically to reuse the same client singleton (_get_client()) and
  the same retry/backoff discipline as extract_from_text() — there was
  no existing free-text generation path to reuse outright, since
  extract_from_text() is hardwired to a JSON schema that a prose answer
  can't fit.
"""

import json
import logging
import time

from google import genai
from google.genai import errors as genai_errors
from google.genai import types
from pydantic import ValidationError

from app.core.config import settings
from app.extraction.extraction_schema import NODE_TYPES, GeminiExtractionResult
from app.extraction.prompt_builder import build_extraction_prompt

logger = logging.getLogger(__name__)

MAX_ATTEMPTS = 3
BACKOFF_SECONDS = (2, 4, 8)
_RETRYABLE_STATUS_CODES = {429, 500, 503}

# Sent via response_json_schema (a plain JSON Schema dict), NOT
# response_schema (the SDK's typed Schema/Type dataclasses).
#
# response_schema goes through google.genai's internal
# _raise_for_unsupported_mldev_properties() check, which unconditionally
# rejects "additionalProperties" — and several other OpenAPI-Schema
# fields — whenever the client isn't running in Vertex AI Enterprise
# mode, REGARDLESS of whether we ourselves ever set that field. This is
# true even for a hand-built types.Schema with additional_properties
# never touched — the SDK adds its own internal representation during
# conversion, so there's no way to avoid it while using response_schema
# at all in Developer API (api_key) mode.
#
# response_json_schema is a separate, newer config field that accepts a
# standard JSON Schema dict close to verbatim (its own docstring lists
# "additionalProperties" as one of the properties it DOES support) and
# skips that internal check entirely. Nullability is expressed with
# "anyOf" here (explicitly supported) rather than typed Schema's
# `nullable=True` flag (which doesn't exist in plain JSON Schema anyway).
def _nullable(schema: dict) -> dict:
    return {"anyOf": [schema, {"type": "null"}]}


_ENTITY_JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "node_type": {"type": "string", "enum": NODE_TYPES},
        "description": _nullable({"type": "string"}),
        "confidence": _nullable({"type": "number"}),
        "evidence_quote": {"type": "string"},
        # Free-form key/value data doesn't map cleanly onto JSON Schema
        # without enumerating every possible key, so we ask for a
        # JSON-encoded string here and decode it back into a dict
        # ourselves before Pydantic validation — see _decode_attributes().
        "attributes": _nullable({"type": "string"}),
    },
    "required": ["name", "node_type", "evidence_quote"],
}

_RELATIONSHIP_JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "source_entity_name": {"type": "string"},
        "target_entity_name": {"type": "string"},
        "relationship_type": {"type": "string"},
        "description": _nullable({"type": "string"}),
        "confidence": _nullable({"type": "number"}),
    },
    "required": ["source_entity_name", "target_entity_name", "relationship_type"],
}

_EXTRACTION_JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "entities": {"type": "array", "items": _ENTITY_JSON_SCHEMA},
        "relationships": {"type": "array", "items": _RELATIONSHIP_JSON_SCHEMA},
    },
    "required": ["entities", "relationships"],
}


class ExtractionError(Exception):
    """Raised when Gemini extraction fails after all retry attempts."""


class GeminiGenerationError(Exception):
    """Raised when Gemini free-text generation fails after all retry
    attempts. Separate from ExtractionError since this is a different
    failure mode (prose generation, not structured extraction) — keeping
    them distinct avoids a caller mistaking one for the other."""


_client: "genai.Client | None" = None


def _get_client() -> "genai.Client":
    global _client
    if _client is None:
        if settings.gemini_use_vertexai:
            if not settings.gcp_project:
                raise ExtractionError(
                    "GEMINI_USE_VERTEXAI is set but GCP_PROJECT is not configured. "
                    "Set it in your .env file."
                )
            # Uses Application Default Credentials (gcloud auth
            # application-default login, or GOOGLE_APPLICATION_CREDENTIALS
            # pointing to a service account JSON) — no API key involved,
            # which is the whole point: this path exists for accounts
            # whose AQ.-prefixed keys are rejected by the Generative
            # Language API.
            _client = genai.Client(
                vertexai=True,
                project=settings.gcp_project,
                location=settings.gcp_location,
            )
        else:
            if not settings.gemini_api_key:
                raise ExtractionError(
                    "GEMINI_API_KEY is not configured. Set it in your .env file."
                )
            _client = genai.Client(api_key=settings.gemini_api_key)
    return _client


def _decode_attributes(parsed_json: dict) -> dict:
    """Gemini returns `attributes` as a JSON-encoded string per the
    schema above — decode it back into a list in place before Pydantic
    validation. Always ends up as a list, never None: GeminiEntity.
    attributes is typed `list[GeminiAttribute]` with no `| None`, so a
    missing/unparseable string must become [], not None — None fails
    validation instead of being treated as "no attributes"."""
    for entity in parsed_json.get("entities", []):
        raw_attrs = entity.get("attributes")
        if isinstance(raw_attrs, str) and raw_attrs.strip():
            try:
                decoded = json.loads(raw_attrs)
                entity["attributes"] = decoded if isinstance(decoded, list) else []
            except json.JSONDecodeError:
                entity["attributes"] = []
        else:
            entity["attributes"] = []
    return parsed_json


def extract_from_text(text_batch: str) -> GeminiExtractionResult:
    """Calls Gemini once per attempt (up to MAX_ATTEMPTS) and returns a
    validated result. Retries on transient API errors (429/500/503) and
    on malformed/invalid JSON output — LLM output is non-deterministic,
    so a second attempt sometimes succeeds where the first didn't.

    Raises ExtractionError if every attempt fails.
    """
    prompt = build_extraction_prompt(text_batch)
    last_error: Exception | None = None

    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            print("=" * 60)
            print("MODEL USED:", settings.gemini_model)
            print("=" * 60)
            print("API KEY PREFIX:", settings.gemini_api_key[:10])
            print("MODEL:", settings.gemini_model)
            client = _get_client()
            response = client.models.generate_content(
                model=settings.gemini_model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_json_schema=_EXTRACTION_JSON_SCHEMA,
                    temperature=0.1,
                ),
            )

            parsed_json = json.loads(response.text)
            parsed_json = _decode_attributes(parsed_json)
            # Authoritative validation on our side — never trust the
            # SDK's structured-output guarantee alone.
            return GeminiExtractionResult.model_validate(parsed_json)

        except genai_errors.APIError as exc:
            last_error = exc
            status_code = getattr(exc, "code", None)
            if status_code in _RETRYABLE_STATUS_CODES and attempt < MAX_ATTEMPTS:
                logger.warning(
                    "Gemini call failed (status=%s), retrying (%d/%d)",
                    status_code, attempt + 1, MAX_ATTEMPTS,
                )
                time.sleep(BACKOFF_SECONDS[attempt - 1])
                continue
            break

        except (json.JSONDecodeError, ValidationError) as exc:
            last_error = exc
            if attempt < MAX_ATTEMPTS:
                logger.warning(
                    "Gemini returned malformed/invalid output, retrying (%d/%d): %s",
                    attempt + 1, MAX_ATTEMPTS, exc,
                )
                time.sleep(BACKOFF_SECONDS[attempt - 1])
                continue
            break

    raise ExtractionError(
        f"Gemini extraction failed after {MAX_ATTEMPTS} attempts: {last_error}"
    ) from last_error


def generate_json(prompt: str, response_json_schema: dict, model_cls: type) -> object:
    """Generic structured-JSON generation. Added for
    CareerIntelligenceService rather than duplicating the retry/backoff
    loop a third time — same client, same MAX_ATTEMPTS/BACKOFF_SECONDS/
    retryable-status discipline as extract_from_text() and generate_text(),
    parameterized by a caller-supplied JSON schema and Pydantic model
    instead of the hardwired extraction schema.

    Raises GeminiGenerationError if every attempt fails.
    """
    last_error: Exception | None = None

    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            client = _get_client()
            response = client.models.generate_content(
                model=settings.gemini_model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_json_schema=response_json_schema,
                    temperature=0.3,
                ),
            )
            parsed_json = json.loads(response.text)
            return model_cls.model_validate(parsed_json)

        except genai_errors.APIError as exc:
            last_error = exc
            status_code = getattr(exc, "code", None)
            if status_code in _RETRYABLE_STATUS_CODES and attempt < MAX_ATTEMPTS:
                logger.warning(
                    "Gemini generate_json failed (status=%s), retrying (%d/%d)",
                    status_code, attempt + 1, MAX_ATTEMPTS,
                )
                time.sleep(BACKOFF_SECONDS[attempt - 1])
                continue
            break

        except (json.JSONDecodeError, ValidationError) as exc:
            last_error = exc
            if attempt < MAX_ATTEMPTS:
                logger.warning(
                    "Gemini generate_json returned malformed/invalid output, "
                    "retrying (%d/%d): %s",
                    attempt + 1, MAX_ATTEMPTS, exc,
                )
                time.sleep(BACKOFF_SECONDS[attempt - 1])
                continue
            break

    raise GeminiGenerationError(
        f"Gemini JSON generation failed after {MAX_ATTEMPTS} attempts: {last_error}"
    ) from last_error


def generate_text(prompt: str) -> str:
    """Calls Gemini for a free-text (non-JSON) response and returns the
    raw answer text. Used by VerseAIService for RAG answers — no
    response_json_schema here since the output is prose, not structured
    entities/relationships.

    Reuses the same client singleton and retry/backoff discipline as
    extract_from_text() (same MAX_ATTEMPTS, same BACKOFF_SECONDS, same
    retryable status codes).

    Raises GeminiGenerationError if every attempt fails.
    """
    last_error: Exception | None = None

    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            client = _get_client()
            response = client.models.generate_content(
                model=settings.gemini_model,
                contents=prompt,
                config=types.GenerateContentConfig(temperature=0.2),
            )
            return response.text

        except genai_errors.APIError as exc:
            last_error = exc
            status_code = getattr(exc, "code", None)
            if status_code in _RETRYABLE_STATUS_CODES and attempt < MAX_ATTEMPTS:
                logger.warning(
                    "Gemini generate_content failed (status=%s), retrying (%d/%d)",
                    status_code, attempt + 1, MAX_ATTEMPTS,
                )
                time.sleep(BACKOFF_SECONDS[attempt - 1])
                continue
            break

    raise GeminiGenerationError(
        f"Gemini text generation failed after {MAX_ATTEMPTS} attempts: {last_error}"
    ) from last_error
