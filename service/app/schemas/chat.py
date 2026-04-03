from typing import List, Optional

from pydantic import BaseModel, Field

class FormItem(BaseModel):
    type: str
    label: str
    meta_data: Optional[dict] = Field(default={}, description="meta data for further request")

class MetaData(BaseModel):
    option: Optional[List[str]] = Field(default=None, description="option for further request")
    form_type: Optional[FormItem] = Field(default=None, description="form_type for further request")

class AskRequest(BaseModel):
    message: str
    session_id: str = Field(default="", description="session id, for history storage")
    type: str = Field(default="text", description="type of message('category')")


