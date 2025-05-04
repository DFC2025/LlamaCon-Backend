from fastapi import APIRouter

from src.web.search import router as search_router

web_router = APIRouter()
web_router.include_router(search_router)