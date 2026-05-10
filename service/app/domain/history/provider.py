from abc import ABC, abstractmethod
from typing import List

from langchain_core.messages import BaseMessage


class HistoryProvider(ABC):
    @abstractmethod
    def get_messages(self, conversation_id: int) -> List[BaseMessage]:
        ...
