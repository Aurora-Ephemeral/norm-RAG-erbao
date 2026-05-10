from datetime import datetime
from typing import Optional, List

from sqlalchemy import BigInteger, DateTime, Index, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.knowledge_base.model import Base
from app.domain.message.model import RagMessage


class RagConversation(Base):
    __tablename__ = "rag_conversation"
    __table_args__ = (
        Index("idx_rag_conversation_user_id", "user_id"),
        Index("idx_rag_conversation_updated_time", "updated_time"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    knowledge_base_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    title: Mapped[str] = mapped_column(String(500), default="", server_default="", nullable=False)
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
    messageList: Mapped[List["RagMessage"]] = relationship("RagMessage", order_by="RagMessage.created_time")
