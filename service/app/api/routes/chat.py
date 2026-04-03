import json

from fastapi import APIRouter, HTTPException
from starlette.responses import StreamingResponse
from typing import AsyncGenerator

from app.schemas import AskRequest
from app.rag import build_rag_chain
from app.util import IntentRouter, sse_headers, generate_sse_message
from app.const import CATEGORY_CLARIFICATION, CATEGORY_META
chain = build_rag_chain()

dummy_context = """
服务合同_2024.pdf · 第3条
第3条 保密义务：乙方承诺在合同期内及合同终止后2年内，
不得向任何第三方披露甲方的商业机密、技术秘密及客户信息。
违者须赔偿甲方不低于50万元人民币的违约金。
"""

async def generate_stream(user_input:str) -> AsyncGenerator[str, None]:
    try:
        async for chunk in chain.astream(input = {"question": user_input, "context": dummy_context}):
            yield f"data: {chunk}\n\n"
        yield "data: [Done]\n\n"
    except Exception as e:
        error_msg = json.dumps({"error": str(e)}, ensure_ascii=False)
        yield error_msg



router = APIRouter(prefix="/chat", tags=["chat"])
intentRouter = IntentRouter()
@router.get("/")
async def root():
    return {"message": "Hello World"}

@router.post("/ask")
async def ask(request: AskRequest) -> StreamingResponse:
    if request.message is None:
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    question = request.message.strip()
    analysis = intentRouter.predict(question)
    if len(analysis["category"]) == 0:
        return StreamingResponse(
            generate_sse_message(CATEGORY_CLARIFICATION, CATEGORY_META, request.session_id),
            media_type="text/event-stream",
            headers=sse_headers()
        )
    return StreamingResponse(
        generate_sse_message(f"当前识别到的分类是:{analysis['category']}", {}, request.session_id),
        media_type="text/event-stream",
        headers=sse_headers()
    )
    # return StreamingResponse(
    #     generate_stream(request.message),
    #     media_type="text/event-stream",
    #     headers=sse_headers()
    # )

@router.get("/session_id")
def session_id():
    return {}
