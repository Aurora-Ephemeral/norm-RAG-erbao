import uuid
from datetime import datetime
from typing import Any, Dict, Optional

from pgvector.sqlalchemy import Vector
from sqlalchemy import BigInteger, DateTime, Integer, String, Text, JSON, func, Computed
from sqlalchemy.dialects.postgresql import UUID, TSVECTOR
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.knowledge_base.model import Base


class RagChunk(Base):
    __tablename__ = "rag_chunk"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    chunk_uuid: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        default=uuid.uuid4,
        server_default=func.uuid_generate_v4(),
        nullable=False,
    )
    document_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    chunk_text: Mapped[str] = mapped_column(Text, nullable=False)
    token_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    char_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    embedding_model: Mapped[str] = mapped_column(String(100), nullable=False)
    embedding: Mapped[Optional[list]] = mapped_column(Vector(1024), nullable=True)
    page_no: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    section_title: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    metadata_json: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    fts_vector: Mapped[Optional[Any]] = mapped_column(
        TSVECTOR,
        Computed("to_tsvector('english', chunk_text)", persisted=True),
        nullable=True,
    )
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
