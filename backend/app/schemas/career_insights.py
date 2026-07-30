from pydantic import BaseModel, Field


class Recommendation(BaseModel):
    """An opinion, not a verified fact — always paired with a reason so
    the frontend can never present it as evidence-backed."""
    item: str
    reason: str


class Highlight(BaseModel):
    """Points at something that already exists in Career Brain (a real
    project/certification name) — the frontend cross-references `name`
    against the actual node to attach its real evidence_quote/filename,
    so a highlight is still evidence-backed even though `reason` is the
    model's framing of why it stands out."""
    name: str
    reason: str


class CareerInsights(BaseModel):
    resume_summary: str
    experience_summary: str = ""
    top_strengths: list[str] = Field(default_factory=list)
    core_skills: list[str] = Field(default_factory=list)
    # Opinions about gaps/weaknesses/next steps — never presented as
    # verified facts pulled from a document. There's no evidence_quote
    # for "you should learn Rust" or "this skill looks underdeveloped".
    weak_skills: list[Recommendation] = Field(default_factory=list)
    missing_skills: list[Recommendation] = Field(default_factory=list)
    learning_suggestions: list[Recommendation] = Field(default_factory=list)
    career_recommendations: list[Recommendation] = Field(default_factory=list)
    project_highlights: list[Highlight] = Field(default_factory=list)
    certification_highlights: list[Highlight] = Field(default_factory=list)
