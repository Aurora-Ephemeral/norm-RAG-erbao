from typing import Any, Dict, Optional

from pydantic import BaseModel


class ChunkCreate(BaseModel):
    document_id: int
    chunk_index: int
    chunk_text: str
    token_count: int = 0
    char_count: int = 0
    embedding_model: str
    page_no: Optional[int] = None
    section_title: Optional[str] = None
    metadata_json: Optional[Dict[str, Any]] = None
