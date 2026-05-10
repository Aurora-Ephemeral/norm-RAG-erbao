from typing import Generic, List, TypeVar, Annotated
from datetime import datetime
from pydantic import BaseModel
from pydantic.functional_serializers import PlainSerializer

T = TypeVar("T")

class PageResult(BaseModel, Generic[T]):
    rows: List[T]
    current: int
    size: int
    total: int

FormattedDateTime = Annotated[
    datetime,
    PlainSerializer(lambda x: x.strftime("%Y-%m-%d %H:%M:%S"), return_type=str)
]