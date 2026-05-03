import json

def sse_headers():
    return {
        "Cache-Control": "no-cache, no-store, must-revalidate",
        "Connection": "keep-alive",
        "X-Accel-Buffering": "no"
    }

def generate_sse_message(msg: str, meta, session_id: str):
    meta = json.dumps({"session_id": session_id, "meta": meta}, ensure_ascii=False)
    msg_json = json.dumps({"content": msg}, ensure_ascii=False)
    yield f"event: clarification\ndata: {meta}\n\n"
    yield f"data: {msg_json}\n\n"
    yield "data: [DONE]\n\n"
