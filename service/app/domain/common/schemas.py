from typing import Generic, List, TypeVar
from pydantic import BaseModel

T = TypeVar("T")

class PageResult(BaseModel, Generic[T]):
    rows: List[T]
    current: int
    size: int
    total: int