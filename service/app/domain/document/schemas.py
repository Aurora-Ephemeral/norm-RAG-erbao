import uuid
from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.domain.document.model import DocStatusEnum


class DocumentBase(BaseModel):
    file_id: int = Field(..., description="Associated file ID")
    knowledge_base_id: int = Field(..., description="Parent knowledge base ID")
    doc_title: Optional[str] = Field(default=None, max_length=500, description="Document title")
    doc_type: Optional[str] = Field(default=None, max_length=64, description="Document type")
    language: Optional[str] = Field(default=None, max_length=32, description="Document language")
    version: int = Field(default=1, gt=0, description="Document version")
    is_latest: bool = Field(default=True, description="Whether this is the latest version")
    doc_status: DocStatusEnum = Field(default=DocStatusEnum.ACTIVE, description="Document status")
    part_type: Optional[str] = Field(default=None, max_length=64, description="Part type for hybrid search filtering (e.g. 螺栓, 板材)")
    standard_no: Optional[str] = Field(default=None, max_length=128, description="Standard number for hybrid search filtering (e.g. GB/T 5782)")
    chunk_count: int = Field(default=0, ge=0, description="Number of chunks")
    token_count: int = Field(default=0, ge=0, description="Number of tokens")
    metadata_json: Optional[Dict[str, Any]] = Field(default=None, description="Extended metadata")


class DocumentCreate(DocumentBase):
    pass


class DocumentUpdate(BaseModel):
    doc_title: Optional[str] = Field(default=None, max_length=500, description="Document title")
    doc_type: Optional[str] = Field(default=None, max_length=64, description="Document type")
    language: Optional[str] = Field(default=None, max_length=32, description="Document language")
    version: Optional[int] = Field(default=None, gt=0, description="Document version")
    is_latest: Optional[bool] = Field(default=None, description="Whether this is the latest version")
    doc_status: Optional[DocStatusEnum] = Field(default=None, description="Document status")
    part_type: Optional[str] = Field(default=None, max_length=64, description="Part type for hybrid search filtering")
    standard_no: Optional[str] = Field(default=None, max_length=128, description="Standard number for hybrid search filtering")
    chunk_count: Optional[int] = Field(default=None, ge=0, description="Number of chunks")
    token_count: Optional[int] = Field(default=None, ge=0, description="Number of tokens")
    metadata_json: Optional[Dict[str, Any]] = Field(default=None, description="Extended metadata")

class DocumentFilter(BaseModel):
    knowledge_base_id: int = Field(..., description="Parent knowledge base ID")
    doc_title: Optional[str] = Field(default=None, max_length=500, description="Document title")
    part_type: Optional[str] = Field(default=None, max_length=64, description="Filter by part type")
    standard_no: Optional[str] = Field(default=None, max_length=128, description="Filter by standard number")



class DocumentInDBBase(DocumentBase):
    id: int
    document_uuid: uuid.UUID
    created_time: datetime
    updated_time: datetime

    model_config = ConfigDict(from_attributes=True)


class Document(DocumentInDBBase):
    pass
