from fastapi import APIRouter

from src.web.chat import router as chat_router

web_router = APIRouter()
web_router.include_router(chat_router, prefix="/chat")
