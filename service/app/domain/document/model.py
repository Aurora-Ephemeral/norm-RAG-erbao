import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional

from sqlalchemy import JSON, BigInteger, Boolean, DateTime, Index, Integer, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.knowledge_base.model import Base


class DocStatusEnum(str, Enum):
    ACTIVE = "ACTIVE"
    PROCESSING = "PROCESSING"
    FAILED = "FAILED"
    DELETED = "DELETED"


class Document(Base):
    __tablename__ = "rag_document"
    __table_args__ = (
        UniqueConstraint("knowledge_base_id", "file_id", name="uk_rag_document_kb_file"),
        UniqueConstraint("document_uuid", name="uk_rag_document_uuid"),
        Index("idx_rag_document_created_at", "created_time"),
        Index("idx_rag_document_doc_status", "doc_status"),
        Index("idx_rag_document_file_id", "file_id"),
        Index("idx_rag_document_kb_id", "knowledge_base_id"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    document_uuid: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        default=uuid.uuid4,
        server_default=func.uuid_generate_v4(),
        nullable=False,
        unique=True,
    )
    file_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    knowledge_base_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    doc_title: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    doc_type: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    language: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    is_latest: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    doc_status: Mapped[str] = mapped_column(String(32), default=DocStatusEnum.ACTIVE, nullable=False)
    chunk_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    token_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
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
