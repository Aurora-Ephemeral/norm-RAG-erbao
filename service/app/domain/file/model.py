import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional

from sqlalchemy import BigInteger, Boolean, CHAR, CheckConstraint, DateTime, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.knowledge_base.model import Base


class StorageTypeEnum(str, Enum):
    S3 = "S3"
    LOCAL = "LOCAL"


class FileStatusEnum(str, Enum):
    UPLOADED = "UPLOADED"
    ACTIVE = "ACTIVE"
    DELETED = "DELETED"



class RawFile(Base):
    __tablename__ = "rag_raw_file"
    __table_args__ = (
        UniqueConstraint("file_uuid", name="uk_rag_raw_file_uuid"),
        UniqueConstraint("file_md5", name="uk_rag_raw_file_md5"),
        CheckConstraint("file_size >= 0", name="rag_raw_file_file_size_check"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    file_uuid: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        default=uuid.uuid4,
        server_default=func.uuid_generate_v4(),
        nullable=False,
        unique=True,
    )
    file_md5: Mapped[str] = mapped_column(CHAR(32), nullable=False, unique=True)
    file_sha256: Mapped[Optional[str]] = mapped_column(CHAR(64), nullable=True)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_ext: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    mime_type: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    file_size: Mapped[int] = mapped_column(BigInteger, nullable=False)
    storage_type: Mapped[str] = mapped_column(String(32), default=StorageTypeEnum.S3, nullable=False)
    storage_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    status: Mapped[str] = mapped_column(String(32), default=FileStatusEnum.UPLOADED, nullable=False)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    metadata_json: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)
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
