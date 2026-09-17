import uuid
from datetime import datetime
from typing import List, Optional, Any, Dict
from sqlalchemy import String, Text, DateTime, ForeignKey, func, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pgvector.sqlalchemy import Vector
from app.core.database import Base


class StudyMaterial(Base):
    __tablename__ = "study_materials"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    source_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="manual",
    )  # "moodle", "q10", "pdf", "manual"
    source_url: Mapped[Optional[str]] = mapped_column(
        String(1024),
        nullable=True,
    )
    raw_content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    cleaned_content: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    # 768-dimensional vector embedding (optimized for Gemini text-embedding-004 zero-cost tier)
    embedding: Mapped[Optional[list[float]]] = mapped_column(
        Vector(768),
        nullable=True,
    )

    metadata_json: Mapped[Dict[str, Any]] = mapped_column(
        JSON,
        default=dict,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="study_materials",
    )
    recall_items: Mapped[List["RecallItem"]] = relationship(
        "RecallItem",
        back_populates="study_material",
        cascade="all, delete-orphan",
    )
