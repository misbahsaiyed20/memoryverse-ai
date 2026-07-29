from pydantic import BaseModel, Field, field_validator


class VerseRequest(BaseModel):
    question: str = Field(..., min_length=1)
    top_k: int = Field(default=5, ge=1, le=20)

    @field_validator("question")
    @classmethod
    def validate_question(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Question cannot be empty.")
        return value


class VerseSource(BaseModel):
    document_id: str | None = None
    filename: str | None = None
    chunk_id: str | None = None
    chunk_index: int | None = None
    distance: float | None = None


class VerseResponse(BaseModel):
    success: bool
    answer: str
    sources: list[VerseSource]