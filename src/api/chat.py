from fastapi import APIRouter, Body
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from src.core.config import settings
from src.core.deps import DBClientDep, OpenAIDep

router = APIRouter()


class ChatRequest(BaseModel):
    msg: str


@router.post("/{chat_id}")
def chat_with_openai(
    chat_id: str,
    openai_client: OpenAIDep,
    supabase_client: DBClientDep,
    body: ChatRequest = Body(...),
):
    msg = body.msg
    chat_history = (
        supabase_client.table("chat_history")
        .select("messages")
        .eq("id", chat_id)
        .execute()
        .data[0]
    )
    chat_history = chat_history["messages"]
    if not chat_history:
        chat_history = [{"role": "user", "content": msg}]
    else:
        chat_history.append({"role": "user", "content": msg})

    def stream_response():
        ass_msg = ""
        response = openai_client.chat.completions.create(
            model=settings.LLM_MODEL,
            messages=chat_history,
            temperature=0.6,
            max_completion_tokens=2048,
            top_p=0.9,
            frequency_penalty=1,
            stream=True,
        )
        for chunk in response:
            content = chunk.choices[0].delta.content
            if content:
                ass_msg += content
                yield content

        chat_history.append({"role": "assistant", "content": ass_msg})
        supabase_client.table("chat_history").update({"messages": chat_history}).eq(
            "id", chat_id
        ).execute()

    return StreamingResponse(stream_response(), media_type="text/plain")
