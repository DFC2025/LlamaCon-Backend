import json
from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from src.core.deps import DBClientDep

router = APIRouter()


templates = Jinja2Templates(directory=str(Path(__file__).parent.parent / "templates"))


@router.get("/new", response_class=HTMLResponse)
async def new_chat(request: Request, supabase_client: DBClientDep):
    response = supabase_client.table("chat_history").insert({}).execute()
    chat = {"id": response.data[0]["id"], "messages": []}
    return templates.TemplateResponse("chat.html", {"request": request, "chat": chat})


@router.get("/{chat_id}", response_class=HTMLResponse)
async def chat(chat_id: str, request: Request, supabase_client: DBClientDep):
    response = (
        supabase_client.table("chat_history").select("*").eq("id", chat_id).execute()
    )
    messages = [
        {
            "role": m["role"],
            "content": json.dumps(m["content"], ensure_ascii=False)[1:-1],
        }
        for m in response.data[0]["messages"]
    ]
    chat = {
        "id": chat_id,
        "messages": messages[::-1],
    }
    return templates.TemplateResponse("chat.html", {"request": request, "chat": chat})
