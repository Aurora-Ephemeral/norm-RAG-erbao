from fastapi import APIRouter
from app.api.routes import chat
from app.api.routes import knowledgebase

api_router = APIRouter()

api_router.include_router(chat.router)
api_router.include_router(knowledgebase.router)
