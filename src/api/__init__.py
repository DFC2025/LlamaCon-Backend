from fastapi import APIRouter

from src.api.save_item import router as save_item_router

api_router = APIRouter()
api_router.include_router(save_item_router, prefix="/items", tags=["items"])
