import uuid
from datetime import datetime
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field, field_validator, ConfigDict


class StudyMaterialBase(BaseModel):
    title: str = Field(
        ...,
        min_length=2,
        max_length=255,
        description="Title or topic of the extracted academic material.",
    )
    source_type: str = Field(
        default="manual",
        pattern=r"^(moodle|q10|canvas|pdf|manual)$",
        description="Origin LMS or source platform.",
    )
    source_url: Optional[str] = Field(
        default=None,
        max_length=1024,
        description="URL of the page where the content was captured.",
    )


class StudyMaterialCreate(StudyMaterialBase):
    raw_content: str = Field(
        ...,
        min_length=10,
        max_length=500000,
        description="Raw text content extracted from DOM or documents.",
    )
    user_id: Optional[uuid.UUID] = Field(
        default=None,
        description="Owner student ID. Defaults to system user if omitted.",
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Structured DOM tags, breadcrumbs, course name, etc.",
    )

    @field_validator("raw_content", "title")
    @classmethod
    def sanitize_strings(cls, v: str) -> str:
        v = v.strip()
        # Remove dangerous null bytes and control characters
        v = "".join(ch for ch in v if ch == "\n" or ch == "\t" or (32 <= ord(ch) <= 126 or ord(ch) > 127))
        return v


class StudyMaterialResponse(StudyMaterialBase):
    id: uuid.UUID
    user_id: uuid.UUID
    cleaned_content: Optional[str] = None
    metadata_json: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
