import uuid
from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.domain.file.model import FileStatusEnum, StorageTypeEnum


class RawFileBase(BaseModel):
    file_md5: str = Field(..., max_length=32, description="MD5 hash of file content")
    file_sha256: Optional[str] = Field(default=None, max_length=64, description="SHA256 hash of file content")
    file_name: str = Field(..., max_length=255, description="Original file name")
    file_ext: Optional[str] = Field(default=None, max_length=32, description="File extension")
    mime_type: Optional[str] = Field(default=None, max_length=128, description="MIME type")
    file_size: int = Field(..., ge=0, description="File size in bytes")
    storage_type: StorageTypeEnum = Field(default=StorageTypeEnum.S3, description="Storage backend type")
    storage_path: str = Field(..., max_length=1024, description="Path or key in storage backend")
    status: FileStatusEnum = Field(default=FileStatusEnum.UPLOADED, description="File lifecycle status")
    is_deleted: bool = Field(default=False, description="Soft delete flag")
    metadata_json: Optional[Dict[str, Any]] = Field(default=None, description="Extended metadata")


class RawFileCreate(RawFileBase):
    pass


class RawFileUpdate(BaseModel):
    file_name: Optional[str] = Field(default=None, max_length=255, description="Original file name")
    storage_path: Optional[str] = Field(default=None, max_length=1024, description="Path or key in storage backend")
    status: Optional[FileStatusEnum] = Field(default=None, description="File lifecycle status")
    is_deleted: Optional[bool] = Field(default=None, description="Soft delete flag")
    metadata_json: Optional[Dict[str, Any]] = Field(default=None, description="Extended metadata")


class RawFileFilter(BaseModel):
    file_name: Optional[str] = Field(default=None, max_length=255, description="Filter by file name (partial match)")


class RawFileInDBBase(RawFileBase):
    id: int
    file_uuid: uuid.UUID
    created_time: datetime
    updated_time: datetime

    model_config = ConfigDict(from_attributes=True)


class RawFile(RawFileInDBBase):
    pass

class RawFileUploadResult(BaseModel):
    file_exist: bool = False
    doc_exist: bool = False
    data: RawFile = Field(default=None, description="RawFile data")
