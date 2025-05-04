from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()


templates = Jinja2Templates(directory=str(Path(__file__).parent.parent / "templates"))


@router.get("/{chat_id}", response_class=HTMLResponse)
async def chat(chat_id: str, request: Request):
    messages = [
        {
            "role": "assistant",
            "content": "Hello! How can I assist you today?",
        },
    ]
    chat = {"id": chat_id, "messages": messages}
    return templates.TemplateResponse("chat.html", {"request": request, "chat": chat})
