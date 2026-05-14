from fastapi import APIRouter
from app.api.routes import chat
from app.api.routes import knowledgebase
from app.api.routes import docuemnt
from app.api.routes import file
from app.api.routes import conversation
api_router = APIRouter(prefix="/api/v1")

api_router.include_router(chat.router)
api_router.include_router(knowledgebase.router)
api_router.include_router(docuemnt.router)
api_router.include_router(file.router)
api_router.include_router(conversation.router)
