from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.domain.message.model import MessageRoleEnum


class Message(BaseModel):
    role: MessageRoleEnum = Field(...)
    content: str = Field(...)


class MessageCreate(Message):
    conversation_id: str = Field(...)


class MessageInDBBase(Message):
    id: int
    conversation_id: str
    created_time: datetime
    model_config = ConfigDict(from_attributes=True)


class MessageResponse(MessageInDBBase):
    pass
