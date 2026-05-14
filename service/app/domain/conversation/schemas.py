from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_serializer
from app.domain.message.schemas import MessageResponse
from app.domain.common.schemas import FormattedDateTime

class Conversation(BaseModel):
    user_id: Optional[int] = Field(default=None)
    knowledge_base_id: Optional[int] = Field(default=None)
    title: str = Field(default="", max_length=500)

class ConversationCreate(Conversation):
    id: str

class ConversationUpdate(BaseModel):
    title: Optional[str] = Field(default=None, max_length=500)



class ConversationInDBBase(Conversation):
    id: str
    created_time: FormattedDateTime
    updated_time: FormattedDateTime
    model_config = ConfigDict(from_attributes=True)

class ConversationResponse(ConversationInDBBase):
    pass

class ConversationDetailResponse(ConversationResponse):
    messageList: list[MessageResponse] = Field(default_factory=list)