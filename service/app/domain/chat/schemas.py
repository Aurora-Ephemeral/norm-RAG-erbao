from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

class FormItem(BaseModel):
    type: str
    label: str
    meta_data: Optional[Dict[str, Any]] = Field(default={}, description="meta data for further request")

class MetaData(BaseModel):
    option: Optional[List[str]] = Field(default=None, description="option for further request")
    form_type: Optional[FormItem] = Field(default=None, description="form_type for further request")

class AskRequest(BaseModel):
    message: str
    session_id: str = Field(default="", description="session id, for history storage")

class QueryProcessing(BaseModel):
    english_query: str
    standard_nos: List[str]
    part_types: List[str]
