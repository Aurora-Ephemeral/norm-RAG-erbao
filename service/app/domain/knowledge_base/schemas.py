from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.domain.knowledge_base.model import (
    RetrievalStrategyEnum,
    StatusEnum,
    VisibilityEnum,
)


class KnowledgeBaseBase(BaseModel):
    kb_name: str = Field(..., max_length=255, description="Knowledge base name")
    description: Optional[str] = Field(default=None, description="Knowledge base description")
    owner_user_id: int = Field(..., description="Owner user ID")
    visibility: VisibilityEnum = Field(
        default=VisibilityEnum.PRIVATE,
        description="Visibility",
    )
    status: StatusEnum = Field(default=StatusEnum.ACTIVE, description="Status")
    document_count: int = Field(default=0, ge=0, description="Document count")
    chunk_count: int = Field(default=0, ge=0, description="Chunk count")
    embedding_model: Optional[str] = Field(
        default="bge-m3",
        max_length=100,
        description="Embedding model",
    )
    chunk_size: Optional[int] = Field(default=500, description="Chunk size")
    chunk_overlap: Optional[int] = Field(default=50, description="Chunk overlap")
    top_k: Optional[int] = Field(default=10, description="Top-K retrieval count")
    retrieval_strategy: RetrievalStrategyEnum = Field(
        default=RetrievalStrategyEnum.VECTOR,
        description="Retrieval strategy",
    )
    metadata_json: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Extended metadata",
    )


class KnowledgeBaseCreate(KnowledgeBaseBase):
    pass


class KnowledgeBaseUpdate(BaseModel):
    kb_name: Optional[str] = Field(default=None, max_length=255, description="Knowledge base name")
    description: Optional[str] = Field(default=None, description="Knowledge base description")
    owner_user_id: Optional[int] = Field(default=None, description="Owner user ID")
    visibility: Optional[VisibilityEnum] = Field(default=None, description="Visibility")
    status: Optional[StatusEnum] = Field(default=None, description="Status")
    document_count: Optional[int] = Field(default=None, ge=0, description="Document count")
    chunk_count: Optional[int] = Field(default=None, ge=0, description="Chunk count")
    embedding_model: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Embedding model",
    )
    chunk_size: Optional[int] = Field(default=None, description="Chunk size")
    chunk_overlap: Optional[int] = Field(default=None, description="Chunk overlap")
    top_k: Optional[int] = Field(default=None, description="Top-K retrieval count")
    retrieval_strategy: Optional[RetrievalStrategyEnum] = Field(
        default=None,
        description="Retrieval strategy",
    )
    metadata_json: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Extended metadata",
    )


class KnowledgeBaseInDBBase(KnowledgeBaseBase):
    id: int
    created_time: datetime
    updated_time: datetime

    model_config = ConfigDict(from_attributes=True)


class KnowledgeBase(KnowledgeBaseInDBBase):
    pass
