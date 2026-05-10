from app.core.config import settings
from sqlalchemy.orm import Session
from app.domain.history.provider import HistoryProvider
from app.crud.MessageCrud import MessageCrud
from app.domain.message.model import MessageRoleEnum
from langchain_core.messages import BaseMessage, AIMessage, HumanMessage
from typing import List

class SlidingWindowProvider(HistoryProvider):
    def __init__(self, 
                 db:Session,
                 window_size: int = settings.last_n_messages,
                ):
        self.window_size = window_size
        self.db = db
    
    def get_messages(self, conversation_id: int) -> List[BaseMessage]:
        # 1. get last n turns messages from db 
        messages = MessageCrud(self.db).get_last_n_messages(conversation_id, self.window_size * 2)
        messages.reverse()
        result = [
            AIMessage(content=m.content) if m.role == MessageRoleEnum.ASSISTANT else HumanMessage(content=m.content)
            for m in messages
        ]
        # 3. return 
        return result