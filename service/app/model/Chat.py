from typing import Optional

from pydantic import BaseModel

class ChatRequest(BaseModel):
    message: str
    system_prompt: Optional[str] = "你是一个公司HR专家"

class ChatResponse(BaseModel):
    answer: str
    model: str = "qwen-max"
