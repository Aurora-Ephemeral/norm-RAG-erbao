from fastapi import APIRouter, Depends, HTTPException
from starlette.responses import StreamingResponse

from app.api.dependencies import get_chat_service
from app.domain.chat.schemas import AskRequest
from app.domain.http.sse import sse_headers
from app.service.ChatService import ChatService

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/ask")
async def ask(
    request: AskRequest,
    service: ChatService = Depends(get_chat_service),
) -> StreamingResponse:
    if not request.message or not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    return StreamingResponse(
        service.ask_stream(request.message.strip(), request.session_id),
        media_type="text/event-stream",
        headers=sse_headers(),
    )
