"""Career Intelligence — the one place in this codebase where Gemini
reasons over already-extracted, already-verified data rather than raw
document text. Database stays the source of truth: this service only
ever sends Gemini names/confidence/frequency that already passed
evidence-quote verification in ExtractionService — never raw chunk text,
never evidence_quote content itself. Fields like resume_summary/
top_strengths/core_skills/project_highlights/certification_highlights
describe what's actually there; weak_skills/missing_skills/
learning_suggestions/career_recommendations are the model's opinion —
kept as Recommendation/Highlight objects (item + reason) so callers can
never present an opinion as a verified fact without its reasoning
attached."""

import logging
from collections import Counter

from sqlalchemy.orm import Session

from app.extraction.gemini_client import GeminiGenerationError, generate_json
from app.schemas.career_insights import CareerInsights
from app.services.career_brain_service import CareerBrainService

logger = logging.getLogger(__name__)

_RECOMMENDATION_SCHEMA = {
    "type": "object",
    "properties": {"item": {"type": "string"}, "reason": {"type": "string"}},
    "required": ["item", "reason"],
}
_HIGHLIGHT_SCHEMA = {
    "type": "object",
    "properties": {"name": {"type": "string"}, "reason": {"type": "string"}},
    "required": ["name", "reason"],
}
_INSIGHTS_JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "resume_summary": {"type": "string"},
        "experience_summary": {"type": "string"},
        "top_strengths": {"type": "array", "items": {"type": "string"}},
        "core_skills": {"type": "array", "items": {"type": "string"}},
        "weak_skills": {"type": "array", "items": _RECOMMENDATION_SCHEMA},
        "missing_skills": {"type": "array", "items": _RECOMMENDATION_SCHEMA},
        "learning_suggestions": {"type": "array", "items": _RECOMMENDATION_SCHEMA},
        "career_recommendations": {"type": "array", "items": _RECOMMENDATION_SCHEMA},
        "project_highlights": {"type": "array", "items": _HIGHLIGHT_SCHEMA},
        "certification_highlights": {"type": "array", "items": _HIGHLIGHT_SCHEMA},
    },
    "required": [
        "resume_summary", "experience_summary", "top_strengths", "core_skills",
        "weak_skills", "missing_skills", "learning_suggestions",
        "career_recommendations", "project_highlights", "certification_highlights",
    ],
}

_EMPTY_INSIGHTS = CareerInsights(
    resume_summary="Upload and extract a document to generate career insights.",
)


class CareerIntelligenceService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.career_brain = CareerBrainService(db)

    def get_insights(self, user_id: int) -> CareerInsights:
        counts = self.career_brain.get_entity_counts(user_id)
        if sum(counts.values()) == 0:
            return _EMPTY_INSIGHTS

        nodes = self.career_brain.get_nodes(user_id)
        prompt = self._build_prompt(nodes)

        try:
            return generate_json(prompt, _INSIGHTS_JSON_SCHEMA, CareerInsights)
        except GeminiGenerationError as exc:
            logger.warning("Career insights generation failed for user_id=%s: %s", user_id, exc)
            return CareerInsights(resume_summary="Insights are temporarily unavailable. Please try again.")

    @staticmethod
    def _build_prompt(nodes: list[dict]) -> str:
        by_type: dict[str, list[dict]] = {}
        for node in nodes:
            by_type.setdefault(node["entity_type"], []).append(node)

        # Frequency (how many times a name recurs) and average confidence
        # are real signals from verified data — passed to Gemini so
        # "weak_skills" is grounded in something concrete (low confidence
        # or a single mention) rather than an unfounded guess. Never
        # includes evidence_quote text itself — only names/numbers.
        lines = []
        for entity_type, items in by_type.items():
            name_counts = Counter(item["name"] for item in items)
            avg_conf: dict[str, list[float]] = {}
            for item in items:
                if item["confidence"] is not None:
                    avg_conf.setdefault(item["name"], []).append(item["confidence"])

            parts = []
            for name, count in sorted(name_counts.items()):
                confs = avg_conf.get(name)
                conf_str = f", avg_confidence={sum(confs) / len(confs):.2f}" if confs else ""
                parts.append(f"{name} (mentions={count}{conf_str})")
            lines.append(f"{entity_type}: {'; '.join(parts)}")

        catalog = "\n".join(lines)

        return f"""You are analyzing a candidate's verified career knowledge base, extracted
from their own uploaded documents. Every item below was independently
confirmed against source text, with how many times it was mentioned and
the extraction's confidence score — treat this as ground truth about what
the candidate has actually done. Do not invent anything not listed below.

{catalog}

Return JSON with exactly these fields:
- resume_summary: 3-4 sentence professional summary using ONLY items above.
- experience_summary: 2-3 sentences on work/internship/organization history
  from the items above (empty string if none present).
- top_strengths: 3-5 short phrases naming the candidate's strongest areas.
- core_skills: the candidate's strongest SKILL/TECHNOLOGY items (highest
  mentions/confidence), 5-8 items.
- weak_skills: 2-4 items already in the list above that show LOW confidence
  or only 1 mention — each with "item" (the exact name from the list) and
  "reason" citing the actual signal (e.g. "mentioned once, confidence 0.4").
  Empty array if nothing qualifies — do not force weak entries.
- missing_skills: 3-5 skills commonly paired with what's listed that are
  NOT in the list, each with "reason" explaining why it's a natural gap.
  Never repeat something already listed above.
- learning_suggestions: 3-5 items, each "item" (a skill/technology) and
  "reason" tying it to the candidate's existing trajectory above.
- career_recommendations: 2-4 items, each a concrete next step (role type,
  certification, project direction) with "reason" grounded in the list.
- project_highlights: pick 1-3 PROJECT names FROM THE LIST ABOVE (exact
  name match required) with "reason" for why each stands out.
- certification_highlights: pick 0-3 CERTIFICATE names FROM THE LIST ABOVE
  (exact name match required) with "reason" for each.

Respond with JSON only, matching the schema exactly."""
