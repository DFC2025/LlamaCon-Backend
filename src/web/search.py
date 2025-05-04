from pathlib import Path
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from src.core.db_client import supabase_client
from src.core.helpers import clean_items
from google import genai
import json
import os
import requests
import markdown
router = APIRouter()
templates = Jinja2Templates(directory=str(Path(__file__).parent.parent / "templates"))
modal_url="https://rajuptvs--search-bar-search.modal.run"


@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    tags = ["Active", "Processing"]

    # get search qery from request
    search_query = request.query_params.get("search", "")
    if search_query:
        response = requests.post(modal_url, params={"query": search_query,"user_id":"dddbe848-2225-42bd-9e5e-44ffa1043ef3"})
        items = response.json()
        items = clean_items(items) # to fix this in modal later 
    else:
        items = []
    
    
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "title": "PocketAI", "items": items, "tags": tags},
    )




@router.get("/item/{item_id}", response_class=HTMLResponse)
async def item_detail(request: Request, item_id: str):
    item = {
        "id": item_id,
        "url": "https://example.com",
        "title": supabase_client.table("shared_content").select("text").eq("id",item_id).execute().data[0]["text"],
        "description": supabase_client.table("documents").select("content").eq("content_id",item_id).execute().data[0]["content"],
        "image": "https://picsum.photos/200/300",
        "siteName": "Example",
        "tags": ["example", "demo", "test"],
        "status": "Processing",
    }
    # supabase_client.storage.from_("content").download(item_id/cleaned_markdown.md)
    return templates.TemplateResponse(
        "item.html", {"request": request, "title": "Item Detail", "item": item}
    )