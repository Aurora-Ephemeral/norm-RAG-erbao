from datetime import datetime
from enum import Enum

from sqlalchemy import BigInteger, DateTime, ForeignKey, Index, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.knowledge_base.model import Base


class MessageRoleEnum(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"


class RagMessage(Base):
    __tablename__ = "rag_message"
    __table_args__ = (
        Index("idx_rag_message_conversation_id", "conversation_id"),
        Index("idx_rag_message_conversation_created", "conversation_id", "created_time"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    conversation_id: Mapped[str] = mapped_column(String(36), ForeignKey("rag_conversation.id"), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
