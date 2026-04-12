from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional

from sqlalchemy import JSON, DateTime, Enum as SqlEnum, Integer, String, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class VisibilityEnum(str, Enum):
    PRIVATE = "PRIVATE"
    PUBLIC = "PUBLIC"
    TEAM = "TEAM"


class StatusEnum(str, Enum):
    ACTIVE = "ACTIVE"
    ARCHIVED = "ARCHIVED"
    DISABLED = "DISABLED"


class RetrievalStrategyEnum(str, Enum):
    VECTOR = "VECTOR"
    HYBRID = "HYBRID"
    KEYWORD = "KEYWORD"


class KnowledgeBase(Base):
    __tablename__ = "rag_knowledge_base"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    kb_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    owner_user_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    visibility: Mapped[VisibilityEnum] = mapped_column(
        SqlEnum(VisibilityEnum),
        default=VisibilityEnum.PRIVATE,
        nullable=False,
    )
    status: Mapped[StatusEnum] = mapped_column(
        SqlEnum(StatusEnum),
        default=StatusEnum.ACTIVE,
        nullable=False,
    )
    document_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    chunk_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    embedding_model: Mapped[Optional[str]] = mapped_column(String(100), default="bge-m3")
    chunk_size: Mapped[Optional[int]] = mapped_column(Integer, default=500)
    chunk_overlap: Mapped[Optional[int]] = mapped_column(Integer, default=50)
    top_k: Mapped[Optional[int]] = mapped_column(Integer, default=10)
    retrieval_strategy: Mapped[RetrievalStrategyEnum] = mapped_column(
        SqlEnum(RetrievalStrategyEnum),
        default=RetrievalStrategyEnum.VECTOR,
        nullable=False,
    )
    metadata_json: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    created_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
