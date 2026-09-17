import uuid
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, field_validator


class TutorQueryRequest(BaseModel):
    query: str = Field(
        ...,
        min_length=3,
        max_length=2000,
        description="Student question or active recall review query.",
    )
    user_id: Optional[uuid.UUID] = Field(
        default=None,
        description="Optional student UUID to scope knowledge retrieval.",
    )
    top_k_context: int = Field(
        default=3,
        ge=1,
        le=8,
        description="Number of relevant knowledge chunks to retrieve.",
    )
    bypass_cache: bool = Field(
        default=False,
        description="Force fresh LLM generation bypassing semantic cache.",
    )

    @field_validator("query")
    @classmethod
    def sanitize_query(cls, v: str) -> str:
        v = v.strip()
        # Filter null bytes
        v = v.replace("\x00", "")
        if not v:
            raise ValueError("Query string cannot be empty after sanitization.")
        return v


class TutorSourceReference(BaseModel):
    material_id: str
    title: str
    source_type: str
    similarity_score: float


class TutorQueryResponse(BaseModel):
    answer: str
    cached: bool
    cache_type: Optional[str] = None  # "exact", "semantic", None
    sources: List[TutorSourceReference] = Field(default_factory=list)
