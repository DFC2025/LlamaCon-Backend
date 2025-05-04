from pathlib import Path
from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from src.core.db_client import supabase_client
from src.core.helpers import clean_items,MODAL_URL,PODCAST_CREATE_URL
from google import genai
import json
import os
import requests
import markdown

router = APIRouter()
templates = Jinja2Templates(directory=str(Path(__file__).parent.parent / "templates"))
 # Replace with actual URL


@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    tags = ["Active", "Processing"]

    # get search qery from request
    search_query = request.query_params.get("search", "")
    if search_query:
        response = requests.post(MODAL_URL, params={"query": search_query,"user_id":"dddbe848-2225-42bd-9e5e-44ffa1043ef3"})
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
        "url": supabase_client.table("shared_content").select("url").eq("id",item_id).execute().data[0]["url"],
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

def get_url_for_podcast(user_id:str):
    
    # check if the podcast exists
    exists= supabase_client.storage.from_('podcast').exists(f'{user_id}/rss_feed/podcast.xml')
    if exists:
        return supabase_client.storage.from_('podcast').get_public_url(f'{user_id}/rss_feed/podcast.xml').rstrip('?')
    
    else:
        return None
@router.get("/profile", response_class=HTMLResponse)
async def profile(request: Request):
    # Example user data, replace with real user info as needed
    user = {
        "name": "Raju Penmatsa",
        "email": "raju.penmatsa@gmail.com",
        "bio": "AI Developer.",
        "avatar": "https://ui-avatars.com/api/?name=Raju+Penmatsa"
    }
    return templates.TemplateResponse(
        "profile.html", {"request": request, "title": "Profile", "user": user}
    )

@router.get("/settings", response_class=HTMLResponse)
async def settings(request: Request):
    # TODO: Replace with real user settings fetch if available
    current_schedule = "daily"
    current_articles_per_digest = 5
    return templates.TemplateResponse(
        "settings.html",
        {
            "request": request,
            "title": "Settings",
            "default_name": "Llamacast",
            "default_description": "A podcast created for you, from your interests by your LlamaBuddy",
            "feed_url": get_url_for_podcast("dddbe848-2225-42bd-9e5e-44ffa1043ef3"),
            "schedule": current_schedule,
            "articles_per_digest": current_articles_per_digest
        },
    )

@router.post("/settings", response_class=HTMLResponse)
async def create_feed(request: Request, name: str = Form(...), description: str = Form(...), schedule: str = Form(...), articles_per_digest: int = Form(...)):
    # You can add more fields as needed
    response = requests.post(
        PODCAST_CREATE_URL,
        params={
            "name": name,
            "description": description,
            "website": "https://llamacast.com",
            "explicit": False,
            "id": "help_me_test_it",
            "schedule": schedule,
            "articles_per_digest": articles_per_digest
        }
    )
    print(response.json())
    
    feed_url = response.json() if response.ok else None
    if feed_url:
        # there is ? at the end of the url, remove it
        feed_url = feed_url.rstrip("?")
    return templates.TemplateResponse(
        "settings.html",
        {
            "request": request,
            "title": "Settings",
            "default_name": name,
            "default_description": description,
            "feed_url": feed_url,
            "schedule": schedule,
            "articles_per_digest": articles_per_digest
        },
    )