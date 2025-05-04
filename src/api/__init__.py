from fastapi import APIRouter

from src.api.chat import router as chat_router
from src.api.save_item import router as save_item_router

api_router = APIRouter()
api_router.include_router(save_item_router, prefix="/items", tags=["items"])
api_router.include_router(chat_router, prefix="/chat", tags=["chat"])
