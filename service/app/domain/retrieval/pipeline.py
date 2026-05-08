from abc import ABC, abstractmethod
from typing import List

from app.domain.chunk.model import RagChunk


class RetrievalPipeline(ABC):
    @abstractmethod
    def search(self, query: str) -> List[RagChunk]:
        ...
